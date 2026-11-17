# Treatment BMHP

## Intent

Let clinic staff define the BMHP consumed by each treatment. A treatment may have multiple BMHP rows, each with its own quantity and written unit, such as Needle `1 CC` and Sarung tangan `1 pcs`.

## Goals

- Add a **Treatment BMHP** menu immediately below **Master BMHP** in **Master Data > Master Treatment**.
- Allow staff to choose an existing treatment from `PRODUK.FMPPRODUK_ID`.
- Allow staff to add, edit, and remove several BMHP rows for that treatment.
- Store the selected BMHP, a positive decimal quantity, and a free-text unit for every row.

## Non-goals

- No stock deduction, inventory movement, price, or cost calculation.
- No changes to the legacy `PRODUK` treatment table.
- No fixed master of units; the unit is entered per row as selected by the user.

## Approaches considered

1. **Free-text unit per relation (selected):** save treatment ID, BMHP ID, quantity, and an editable unit. This supports both `1 CC` and `1 pcs` immediately without assuming the existing `PRODUK_UNIT` values cover clinical usage.
2. **Existing product-unit selection:** consistent with legacy product units, but can block valid units such as CC if they are not present in that master.

## Design

- Add a `TreatmentBMHP` table with a foreign key to `BMHP`, `treatment_id` as the existing `PRODUK.FMPPRODUK_ID` string, `jumlah` as a positive decimal, and `satuan` as required text up to 30 characters.
- Enforce one row per treatment, BMHP, and unit to prevent duplicate entries with the same unit; the quantity can be updated instead.
- Create a page with a treatment selector and a list of that treatment's BMHP rows. The input area includes a BMHP selector, quantity field, and unit field, with save, edit, and delete actions.
- Treatment names are read from the existing `PRODUK` table; they remain managed by the existing Master Treatment page.
- Add a role-controlled navigation entry by copying the same privileges used by **Master BMHP**.

## Major UI decisions

- The treatment picker is the focal control. Reason: every relationship is scoped to one selected treatment.
- BMHP rows are shown as a simple table. Reason: staff needs to verify consumables, quantities, and units at a glance.
- Unit stays a labelled text field. Reason: it reflects clinical notation without forcing unconfirmed standardization.
- Dials: ENERGY 1 / RHYTHM 1 / MOTION 1. Reason: this is a focused clinical administration workflow and needs no decorative motion.

## Constraints

- The migration changes the shared SQL Server schema and should be applied only after a database backup.
- The relation keeps the existing treatment ID as text because `PRODUK` is a legacy SQL table not managed by Django migrations.
