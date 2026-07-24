# MCU TODO List

## Current Phase: BUILDER (GREEN)

### In Progress
- [ ] **Journal Entries Parser**: Fix amount calculation (returning €75M, need €28.5M) - 2/4 tests passing

### Next Steps (Priority Order)
1. [ ] **Journal Entries**: Debug debit/credit calculation logic
2. [ ] **OTE Detail**: Implement aggregation by [product, currency, maturity_date]
3. [ ] **CSA Collateral**: Fix test file path format (use forward slashes)
4. [ ] Run all 14 tests → GREEN phase complete
5. [ ] REFACTOR phase for all 3 parsers
6. [ ] Integration test: Complete load → validate £65.11M total

## Completed ✓
- [x] ANALYST: Journal Entries CSV structure analysis
- [x] ANALYST: OTE Detail duplicate constraint investigation
- [x] ANALYST: CSA Collateral file format investigation
- [x] ARCHITECT: Journal Entries design
- [x] ARCHITECT: OTE Detail aggregation design
- [x] ARCHITECT: CSA Collateral design
- [x] TESTER: Write 14 failing tests (RED phase)
- [x] BUILDER: 4 parsers working (MC CEL/CET, PnS, SocGen)

## Test Status (14 total)

### Journal Entries (4 tests)
- [x] test_filters_payment_types_correctly ✓
- [x] test_returns_correct_structure ✓
- [ ] test_extracts_correct_total_eur_amount (€75M vs €28.5M)
- [ ] test_converts_to_correct_gbp_equivalent

### OTE Detail (4 tests)
- [ ] test_aggregates_trades_into_positions
- [ ] test_no_duplicate_position_keys
- [ ] test_dominant_product_has_many_maturities
- [ ] test_includes_maturity_date_in_output

### CSA Collateral (5 tests)
- [ ] test_uses_correct_skiprows_value
- [ ] test_uses_correct_column_names
- [ ] test_matches_entity_names_correctly
- [ ] test_calculates_net_collateral
- [ ] test_does_not_multiply_by_million

### Integration (1 test)
- [ ] test_all_parsers_load_without_errors

## Target: £65.11M Reconciliation
```
BNP MC (CEL + CET):     £30.40M ✓
BNP OTE:                £10.60M (pending)
BNP Journal Entries:    £23.51M (pending)
CSA Collateral:         £11.72M (pending)
SocGen:                 -£11.12M ✓
Total:                  £65.11M
```
