# Master BMHP

## Intent

Provide a master list of Bahan Medis Habis Pakai (BMHP) from the existing **Master Data > Master Treatment** navigation, so staff can maintain BMHP names now and link them to treatments in a later change.

## Goals

- Add a **Master BMHP** item beneath **Master Treatment**.
- Store and maintain BMHP names in a dedicated SQL Server table.
- Provide a focused page to list, add, edit, and delete BMHP names.
- Register the navigation entry in the existing property and privilege tables, so access remains controlled by the current role mechanism.

## Non-goals

- No treatment-to-BMHP relationship in this change.
- No stock, unit, cost, or quantity fields yet.
- No changes to existing treatment or product tables.

## Approaches considered

1. **Dedicated BMHP table (selected):** a Django-managed `BMHP` table with `id` and a unique `nama_bmhp` value. This is the selected approach because the master data is persistent and ready for a later treatment relation.
2. **Menu and page only:** faster to show, but cannot save BMHP names and would be discarded when persistence is added.

## Design

- Add a `dashboard.BMHP` Django model mapped to a new `BMHP` table.
- Fields: numeric primary key `id`; `nama_bmhp` (required, maximum 150 characters, unique); and automatic creation/update timestamps for auditability.
- Add a `master_bmhp/` route and JSON endpoints for list, create, update, and delete operations.
- Reuse the current authenticated-page pattern, navigation context, Bootstrap styling, CSRF protection, and role-driven navbar data.
- The page presents one table headed **Nama BMHP**, a labelled name field, and specific **Tambah**, **Simpan perubahan**, and **Hapus** actions. Empty, validation-error, and loading states explain the next action.
- Add the navigation row under the existing **Master Treatment** parent in `PROPERTIES_NAVBAR`; grant it only through the existing `PRIVILEGE_NAVBAR` mechanism rather than exposing it to every user automatically.

## Major UI decisions

- The page follows the existing application shell so it feels native to IMMODERMA. Reason: users already navigate this administrative system through its Bootstrap menu and forms.
- The only initial field is **Nama BMHP**. Reason: it matches the requested scope and avoids inventing unconfirmed medical-supply attributes.
- A conventional editable data table is used. Reason: users need to scan and maintain a small master list, not analyse metrics.
- Dials: ENERGY 1 / RHYTHM 1 / MOTION 1. Reason: this is a high-clarity clinical administration screen; no decorative animation is needed.

## Constraints and remaining decisions

- Creating the database migration changes the shared SQL Server schema and requires a backup before it is applied.
- The database menu record needs the exact existing `Master Treatment` parent ID, which will be read from the configured database during implementation.
- Existing privilege assignments remain unchanged until an administrator grants the new menu to a role.
