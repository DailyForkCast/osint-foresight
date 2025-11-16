#!/usr/bin/env python3
"""
Think Tank Consensus Tracker v2.0 (SQLite)
CORRECTED FOR OSINT FORESIGHT DATABASE SCHEMA
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json
from tqdm import tqdm

from config_sqlite import CONFIG
from utils_sqlite import (
    get_db_connection, create_sqlite_functions, create_sqlite_indexes,
    preflight_checks, save_results, normalize_entity, get_source_weight, logger
)

def run_consensus_analysis():
    """Enhanced think tank consensus analysis - SQLite version with correct schema"""
    logger.info("="*50)
    logger.info("STARTING THINK TANK CONSENSUS ANALYSIS v2.0 (SQLite)")
    logger.info("="*50)

    conn = get_db_connection()

    try:
        # Register custom functions
        create_sqlite_functions(conn)

        # Run preflight checks
        preflight_results = preflight_checks(conn)
        if preflight_results['documents_with_content'] < 100:
            logger.warning("Less than 100 documents with content - results may be limited")

        # Create indexes
        create_sqlite_indexes(conn)

        # Step 1: Entity aggregation (CORRECTED: entity_text not entity_name for document_entities)
        logger.info("Step 1: Aggregating entities across sources...")

        consensus_query = f"""
        WITH normalized_entities AS (
            SELECT
                entity_text as entity_name,
                entity_type,
                document_id,
                NULL as report_id,
                'document' as source_table
            FROM document_entities
            WHERE entity_text IS NOT NULL
              AND entity_text != ''
              AND entity_type IN ('ORG', 'PERSON', 'GPE', 'TECH', 'LOC')

            UNION ALL

            SELECT
                entity_name,
                entity_type,
                NULL as document_id,
                report_id,
                'report' as source_table
            FROM report_entities
            WHERE entity_name IS NOT NULL
              AND entity_name != ''
              AND entity_type IN ('ORG', 'PERSON', 'GPE', 'TECH', 'LOC')

            UNION ALL

            SELECT
                me.name as entity_name,
                me.entity_type,
                mde.doc_id as document_id,
                NULL as report_id,
                'mcf' as source_table
            FROM mcf_entities me
            JOIN mcf_document_entities mde ON me.entity_id = mde.entity_id
            WHERE me.name IS NOT NULL
              AND me.name != ''
              AND me.entity_type IN ('ORG', 'PERSON', 'GPE', 'TECH', 'LOC')
        ),
        entity_stats AS (
            SELECT
                entity_name,
                entity_type,
                COUNT(DISTINCT COALESCE(document_id, report_id)) as total_mentions,
                COUNT(DISTINCT source_table) as source_diversity,
                GROUP_CONCAT(DISTINCT source_table) as source_types,
                COUNT(DISTINCT document_id) as doc_mentions,
                COUNT(DISTINCT report_id) as report_mentions
            FROM normalized_entities
            GROUP BY entity_name, entity_type
            HAVING COUNT(DISTINCT COALESCE(document_id, report_id)) >= {CONFIG['min_consensus_mentions']}
        )
        SELECT
            entity_name,
            entity_type,
            total_mentions,
            source_diversity,
            source_types,
            doc_mentions,
            report_mentions,
            CASE
                WHEN has_chinese(entity_name) = 1 THEN 'Chinese'
                ELSE 'English'
            END as language
        FROM entity_stats
        ORDER BY total_mentions DESC, source_diversity DESC
        LIMIT 1000
        """

        df_consensus_raw = pd.read_sql_query(consensus_query, conn)
        logger.info(f"Found {len(df_consensus_raw)} entities before normalization")

        # Step 2: Apply entity normalization
        logger.info("Step 2: Normalizing and merging similar entities...")

        df_consensus_raw['normalized_name'] = df_consensus_raw['entity_name'].apply(
            lambda x: normalize_entity(x) if x else x
        )

        # Group by normalized name
        df_consensus = df_consensus_raw.groupby(['normalized_name', 'entity_type']).agg({
            'total_mentions': 'sum',
            'source_diversity': 'max',
            'doc_mentions': 'sum',
            'report_mentions': 'sum',
            'language': 'first',
            'entity_name': lambda x: list(x)[:10]  # Keep variants for later
        }).reset_index()

        # Rename columns - rename list column first, then normalized_name
        df_consensus.rename(columns={
            'entity_name': 'entity_variants',  # Rename list column first
            'normalized_name': 'entity_name'   # Then rename normalized_name
        }, inplace=True)
        df_consensus = df_consensus.sort_values('total_mentions', ascending=False)

        logger.info(f"After normalization: {len(df_consensus)} unique entities")

        # Step 3: Extract context snippets (CORRECTED: content_text not content)
        logger.info("Step 3: Extracting context snippets...")

        context_results = []
        for idx, row in tqdm(df_consensus.head(50).iterrows(),
                           total=min(50, len(df_consensus)),
                           desc="Extracting contexts"):

            # Get entity variants (list of original names) or use normalized name
            entity_variations = row['entity_variants'] if isinstance(row.get('entity_variants'), list) else [row['entity_name']]

            for variant in entity_variations[:3]:
                # Skip if variant is not a string (e.g., Series object)
                if not isinstance(variant, str):
                    continue
                # CORRECTED: content_text, publisher_org, publication_date
                context_query = """
                SELECT
                    ? as entity_name,
                    d.publisher_org as source,
                    d.title,
                    d.publication_date as created_date,
                    SUBSTR(
                        d.content_text,
                        MAX(1, INSTR(LOWER(d.content_text), LOWER(?)) - 200),
                        400
                    ) as context
                FROM documents d
                WHERE LOWER(d.content_text) LIKE '%' || LOWER(?) || '%'
                  AND d.content_text IS NOT NULL
                ORDER BY d.publication_date DESC
                LIMIT 3
                """

                try:
                    contexts = pd.read_sql_query(
                        context_query,
                        conn,
                        params=(row['entity_name'], variant, variant)
                    )

                    if not contexts.empty:
                        context_results.extend(contexts.to_dict('records'))
                        break
                except Exception as e:
                    logger.warning(f"Context extraction failed for {variant}: {e}")

        if context_results:
            context_df = pd.DataFrame(context_results)
            save_results(context_df, 'consensus_contexts.csv')

        # Step 4: Calculate weighted scores
        logger.info("Step 4: Calculating weighted consensus scores...")

        entity_list = df_consensus['entity_name'].head(100).tolist()

        if entity_list:
            placeholders = ','.join(['?' for _ in entity_list])
            # CORRECTED: entity_text, publisher_org
            source_query = f"""
            SELECT DISTINCT
                de.entity_text as entity_name,
                d.publisher_org as source
            FROM document_entities de
            JOIN documents d ON de.document_id = d.id
            WHERE de.entity_text IN ({placeholders})
            """

            df_sources = pd.read_sql_query(source_query, conn, params=entity_list)

            def calculate_weighted_score(entity_name):
                sources = df_sources[df_sources['entity_name'] == entity_name]['source'].tolist()
                weights = [get_source_weight(s) for s in sources]
                return np.mean(weights) if weights else 0.5

            df_consensus['credibility_score'] = df_consensus['entity_name'].apply(calculate_weighted_score)
        else:
            df_consensus['credibility_score'] = 0.5

        df_consensus['weighted_mentions'] = df_consensus['total_mentions'] * df_consensus['credibility_score']
        df_consensus = df_consensus.sort_values('weighted_mentions', ascending=False)

        # Step 5: Statistical validation
        logger.info("Step 5: Statistical validation...")

        mention_mean = df_consensus['total_mentions'].mean()
        mention_std = df_consensus['total_mentions'].std()
        df_consensus['z_score'] = (df_consensus['total_mentions'] - mention_mean) / mention_std if mention_std > 0 else 0
        df_consensus['statistically_significant'] = df_consensus['z_score'].abs() > 2

        # Step 6: Generate visualizations
        logger.info("Step 6: Creating visualizations...")

        fig, axes = plt.subplots(2, 2, figsize=(15, 12))

        # Plot 1: Top entities
        top_20 = df_consensus.head(20)
        axes[0, 0].barh(range(len(top_20)), top_20['total_mentions'])
        axes[0, 0].set_yticks(range(len(top_20)))
        axes[0, 0].set_yticklabels([str(e)[:30] for e in top_20['entity_name']])
        axes[0, 0].set_xlabel('Total Mentions')
        axes[0, 0].set_title('Top 20 Entities by Consensus')
        axes[0, 0].invert_yaxis()

        # Plot 2: Entity type distribution
        type_dist = df_consensus['entity_type'].value_counts()
        axes[0, 1].pie(type_dist.values, labels=type_dist.index, autopct='%1.1f%%')
        axes[0, 1].set_title('Entity Type Distribution')

        # Plot 3: Language distribution
        lang_dist = df_consensus['language'].value_counts()
        axes[1, 0].bar(lang_dist.index, lang_dist.values)
        axes[1, 0].set_xlabel('Language')
        axes[1, 0].set_ylabel('Count')
        axes[1, 0].set_title('Entity Language Distribution')

        # Plot 4: Credibility distribution
        axes[1, 1].hist(df_consensus['credibility_score'], bins=20, edgecolor='black')
        axes[1, 1].set_xlabel('Credibility Score')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].set_title('Source Credibility Distribution')

        plt.tight_layout()
        plt.savefig(f"{CONFIG['output_dir']}/consensus_visualizations.png",
                   dpi=300, bbox_inches='tight')
        plt.close()

        # Step 7: Generate reports
        logger.info("Step 7: Generating reports...")

        save_results(df_consensus, 'consensus_analysis_weighted.csv')

        summary = {
            'analysis_date': datetime.now().isoformat(),
            'database': 'SQLite - OSINT Foresight',
            'total_unique_entities': len(df_consensus),
            'high_consensus_entities': df_consensus[
                df_consensus['source_diversity'] >= 2
            ].head(10)['entity_name'].tolist(),
            'statistically_significant': df_consensus[
                df_consensus['statistically_significant']
            ].head(10)['entity_name'].tolist(),
            'chinese_entities': df_consensus[
                df_consensus['language'] == 'Chinese'
            ].head(10)['entity_name'].tolist(),
            'highest_credibility': df_consensus.nlargest(
                10, 'credibility_score'
            )['entity_name'].tolist(),
            'statistics': {
                'mean_mentions': float(mention_mean),
                'std_mentions': float(mention_std),
                'median_credibility': float(df_consensus['credibility_score'].median())
            }
        }

        with open(f"{CONFIG['output_dir']}/consensus_summary.json", 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        logger.info("✅ CONSENSUS ANALYSIS COMPLETE")
        logger.info(f"Generated files in {CONFIG['output_dir']}:")
        logger.info("  - consensus_analysis_weighted.csv")
        logger.info("  - consensus_contexts.csv")
        logger.info("  - consensus_visualizations.png")
        logger.info("  - consensus_summary.json")

        return df_consensus

    except Exception as e:
        logger.error(f"Consensus analysis failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    run_consensus_analysis()
