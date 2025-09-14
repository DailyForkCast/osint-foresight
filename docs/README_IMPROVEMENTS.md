

## Recent Improvements (September 2025)

Major enhancements have been implemented following a comprehensive review:

### Performance & Reliability
- **Advanced Rate Limiting**: Intelligent API rate management with burst control
- **Transaction-Safe Operations**: ACID compliance for all configuration changes
- **Schema Validation**: Complete JSON schemas for all 95+ artifacts

### Global Coverage
- **Region-Agnostic Design**: Removed EU-specific biases
- **Dynamic Source Selection**: Automatic selection of best data sources per country
- **Terminology Standardization**: Neutral language for all regions

### Data Quality
- **Date Standardization**: All dates in ISO 8601 format
- **Confidence Normalization**: Unified 0-1 scoring with labels
- **ID Standardization**: Consistent ROR/LEI/GRID/ORCID formatting

### Documentation
- See `docs/improvements/` for detailed documentation
- Integration guide at `docs/guides/INTEGRATION_GUIDE.md`
- Review artifacts in `artifacts/_review/CLAUDE_REVIEW/`

### New Utilities
- `src/utils/rate_limiter.py` - API rate limiting
- `src/utils/standardization.py` - Data standardization
- `src/utils/regional_adapter.py` - Regional adaptation
- `scripts/promote_hubs.py` - Safe hub promotion
