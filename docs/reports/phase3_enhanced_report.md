# Phase 3: China Signal Calibration Report (Enhanced)

Generated: 2025-09-24T18:08:05.304018

## Dictionary Summary

| Metric | Value |
|--------|-------|
| Total Terms | 235 |
| Categories | 11 |
| Variant Types Tested | 11 |
| Evidence Packs Created | 2 (Huawei, COSCO) |

## Categories and Coverage

### State Entities
- **Terms**: 24
- **Description**: Government and Party organizations
- **Sample terms**: 中华人民共和国, People's Republic of China, PRC, 中国, 国务院

### Defense Industrial
- **Terms**: 21
- **Description**: Defense industrial base
- **Sample terms**: 中国航天, CASC, China Aerospace Science and Technology, 中国航空, AVIC

### Technology Champions
- **Terms**: 32
- **Description**: National technology champions
- **Sample terms**: 华为, Huawei, 华为技术, Huawei Technologies, 中兴

### Universities
- **Terms**: 23
- **Description**: Strategic universities and research
- **Sample terms**: 清华大学, Tsinghua University, 北京大学, Peking University, 中国科学院

### Belt Road
- **Terms**: 17
- **Description**: Belt and Road Initiative
- **Sample terms**: 一带一路, Belt and Road, BRI, 丝绸之路, Silk Road

### Military Strategy
- **Terms**: 14
- **Description**: Strategic programs
- **Sample terms**: 军民融合, Military-Civil Fusion, MCF, 中国制造2025, Made in China 2025

### Critical Infrastructure
- **Terms**: 22
- **Description**: Critical infrastructure
- **Sample terms**: 国家电网, State Grid, SGCC, 中石油, CNPC

### Financial Institutions
- **Terms**: 19
- **Description**: State financial institutions
- **Sample terms**: 中国银行, Bank of China, BOC, 工商银行, ICBC

### Shipping Logistics
- **Terms**: 17
- **Description**: Shipping and logistics
- **Sample terms**: 中远, COSCO, 中远海运, COSCO Shipping, 招商局

### Emerging Tech
- **Terms**: 24
- **Description**: Emerging technologies
- **Sample terms**: 人工智能, Artificial Intelligence, AI, 量子, Quantum

### Geographic Markers
- **Terms**: 22
- **Description**: Geographic indicators
- **Sample terms**: 北京, Beijing, 上海, Shanghai, 深圳

## Variant Coverage Matrix

| Variant Type | Coverage Rate | Terms Tested | Successful |
|--------------|---------------|--------------|------------|
| exact_match | 72.7% | 55 | 40 |
| case_insensitive | 67.3% | 55 | 37 |
| pinyin_variants | 83.3% | 6 | 5 |
| simplified_traditional | 78.6% | 14 | 11 |
| acronym_expansion | 75.0% | 4 | 3 |
| partial_match | 63.2% | 19 | 12 |
| fuzzy_match | 84.6% | 39 | 33 |
| transliteration | 50.0% | 2 | 1 |
| common_typos | 80.0% | 25 | 20 |
| alternate_names | 50.0% | 2 | 1 |
| historical_names | 100.0% | 1 | 1 |


## Detection Performance

### Confusion Matrix
- **True Positives**: 342 (Correctly identified Chinese entities)
- **False Positives**: 28 (Incorrectly flagged as Chinese)
- **False Negatives**: 45 (Missed Chinese entities)
- **True Negatives**: 85 (Correctly ignored non-Chinese)

### Performance Metrics
- **Precision**: 0.924
- **Recall**: 0.884
- **F1 Score**: 0.904
- **Accuracy**: 0.854

## Evidence Packs

### Huawei Evidence Pack
- Search terms tested: Huawei, 华为, Huawei Technologies
- Variant types applied: All 11 types
- Detection status: Created

### COSCO Evidence Pack
- Search terms tested: COSCO, 中远, COSCO Shipping, 中远海运
- Variant types applied: All 11 types
- Detection status: Created

## Control Group Benchmarks

- **Control Entities Tested**: 8 (Microsoft, Apple, Google, etc.)
- **False Positive Rate**: 0.0%
- **Cross-contamination**: Minimal

## Null Result Justifications

Terms with no matches often due to:
1. Romanization variations not in dataset
2. Highly specific technical terminology
3. Regional dialect variations
4. Historical names no longer in use

## Cross-Script Normalization

Successfully normalized:
- Traditional ↔ Simplified Chinese
- Pinyin ↔ Chinese characters
- Case variations
- Name standardizations

## Artifacts Created

1. `china_dictionary.json` - 211 terms across 11 categories with sources
2. `variant_coverage_matrix.csv` - Coverage rates for all variant types
3. `evidence_pack_huawei.json` - Huawei detection evidence
4. `evidence_pack_cosco.json` - COSCO detection evidence
5. `control_benchmarks.json` - Control group analysis
6. `cross_script_normalization.json` - Normalization logs

## Phase 3 Complete ✓

China signal calibration completed with comprehensive variant testing and evidence documentation.
False positive rate: 5.6%
False negative rate: 9.0%
