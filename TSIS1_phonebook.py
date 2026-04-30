import csv
import json
import sys
from datetime import date

from connect import get_connection, get_cursor

R = "\033[0m"
BOLD  = "\033[1m"
CYAN  = "\033[96m"
GREEN = "\033[92m"
YEL   = "\033[93m"
RED   = "\033[91m"
DIM   = "\033[2m"

def c(text, col): return f"{col}{text}{R}"
def header(t):
    print(); print(c("─"*52, CYAN)); print(c(f"  {t}", BOLD+CYAN)); print(c("─"*52, CYAN))
def pause():
    input(c("\n  Press Enter to continue…", DIM))

def _fetchall(sql, params=()):
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(sql, params)
            return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()

def _execute(sql, params=(), commit=True):
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(sql, params)
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def get_groups():
    return _fetchall("SELECT id, name FROM groups ORDER BY name")

def get_or_create_group(name: str) -> int:
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(
                "INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
                (name,)
            )
            cur.execute("SELECT id FROM groups WHERE name = %s", (name,))
            gid = cur.fetchone()["id"]
        conn.commit()
        return gid
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def get_phones(contact_id: int):
    return _fetchall(
        "SELECT id, phone, type FROM phones WHERE contact_id=%s ORDER BY id",
        (contact_id,)
    )

def db_add_phone(contact_id: int, phone: str, ptype: str):
    _execute(
        "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
        (contact_id, phone, ptype)
    )

def delete_phone(phone_id: int):
    _execute("DELETE FROM phones WHERE id=%s", (phone_id,))

def get_contact_by_name(name: str):
    rows = _fetchall("SELECT * FROM contacts WHERE name=%s", (name,))
    return rows[0] if rows else None

def get_contact_by_id(cid: int):
    rows = _fetchall(
        ,
        (cid,)
    )
    return rows[0] if rows else None

def count_contacts(group_id=None):
    if group_id:
        rows = _fetchall("SELECT COUNT(*) FROM contacts WHERE group_id=%s", (group_id,))
    else:
        rows = _fetchall("SELECT COUNT(*) FROM contacts")
    return rows[0]["count"]

def get_page(limit: int, offset: int):
    
    return _fetchall("SELECT * FROM get_contacts_page(%s, %s)", (limit, offset))

def get_by_group(group_id: int, sort_by: str = "name"):
    col = sort_by if sort_by in ("name", "birthday", "created_at") else "name"
    sql = f
    return _fetchall(sql, (group_id,))

def search_by_email(pattern: str):
    sql = 
    return _fetchall(sql, (f"%{pattern}%",))

def search_all_fields(query: str):
    
    return _fetchall("SELECT * FROM search_contacts(%s)", (query,))

def add_contact_extended(name, email=None, birthday=None, group_id=None) -> int:
    conn = get_connection()
    try:
        with get_cursor(conn) as cur:
            cur.execute(
                ,
                (name, email, birthday, group_id)
            )
            cid = cur.fetchone()["id"]
        conn.commit()
        return cid
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def update_contact_extended(cid, name, email=None, birthday=None, group_id=None):
    _execute(
        "UPDATE contacts SET name=%s, email=%s, birthday=%s, group_id=%s WHERE id=%s",
        (name, email, birthday, group_id, cid)
    )

def call_add_phone(contact_name: str, phone: str, ptype: str):
    _execute("CALL add_phone(%s, %s, %s)", (contact_name, phone, ptype))

def call_move_to_group(contact_name: str, group_name: str):
    _execute("CALL move_to_group(%s, %s)", (contact_name, group_name))

PAGE_SIZE = 5

def fmt(contact: dict, idx: int = None) -> str:
    pre   = f"  {idx:>3}. " if idx else "       "
    bday  = str(contact.get("birthday") or "—")
    group = contact.get("group_name") or "—"
    email = contact.get("email") or "—"
    ph    = contact.get("phones") or "—"
    return (
        f"{pre}{c(contact['name'], BOLD)}  [{c(group, YEL)}]\n"
        f"       📞  {ph}\n"
        f"       ✉   {email}\n"
        f"       🎂  {bday}"
    )

def print_list(contacts: list):
    if not contacts:
        print(c("  (nothing found)", DIM)); return
    for i, ct in enumerate(contacts, 1):
        print(fmt(ct, i)); print()

def pick_sort() -> str:
    print(f"\n  Sort:  {c('1',CYAN)} name   {c('2',CYAN)} birthday   {c('3',CYAN)} date added")
    return {"1": "name", "2": "birthday", "3": "created_at"}.get(input("  > ").strip(), "name")

def pick_group() -> int | None:
    groups = get_groups()
    print()
    for g in groups:
        print(f"    {g['id']}. {g['name']}")
    print("    0. (no group)")
    val = input("  Group id: ").strip()
    if val == "0" or not val:
        return None
    try:
        gid = int(val)
        if any(g["id"] == gid for g in groups):
            return gid
    except ValueError:
        pass
    return None

def add_phones_loop(contact_id: int):
    while True:
        phone = input("  Phone (blank to stop): ").strip()
        if not phone:
            break
        pt = input("  Type [home/work/mobile] (default mobile): ").strip().lower()
        if pt not in ("home", "work", "mobile"):
            pt = "mobile"
        db_add_phone(contact_id, phone, pt)
        print(c(f"  ✓ Added {phone} ({pt})", GREEN))

def paginated_browse(group_id=None, sort_by="name"):
    offset = 0
    while True:
        if group_id:
            all_contacts = get_by_group(group_id, sort_by)
            total = len(all_contacts)
            page  = all_contacts[offset: offset + PAGE_SIZE]
        else:
            total = count_contacts()
            page  = get_page(PAGE_SIZE, offset)

        cur_page  = offset // PAGE_SIZE + 1
        total_pgs = max(1, (total - 1) // PAGE_SIZE + 1)

        header(f"Contacts  (page {cur_page}/{total_pgs})  sorted: {sort_by}")
        print_list(page)
        print(c(f"  {offset+1}–{min(offset+PAGE_SIZE, total)} of {total}", DIM))
        print()

        nav = []
        if offset + PAGE_SIZE < total: nav.append(c("[n]", GREEN) + "ext")
        if offset > 0:                 nav.append(c("[p]", GREEN) + "rev")
        nav.append(c("[q]", RED) + "uit")
        print("  " + "  ".join(nav))

        cmd = input("  > ").strip().lower()
        if   cmd == "n" and offset + PAGE_SIZE < total: offset += PAGE_SIZE
        elif cmd == "p" and offset > 0:                  offset -= PAGE_SIZE
        elif cmd == "q":                                  break

def menu_search():
    header("Search & Filter")
    print(f"  {c('1',CYAN)} Full search (name / email / phone)")
    print(f"  {c('2',CYAN)} Search by email")
    print(f"  {c('3',CYAN)} Filter by group  (paginated)")
    ch = input("  > ").strip()

    if ch == "1":
        q = input("  Query: ").strip()
        print_list(search_all_fields(q))
        pause()
    elif ch == "2":
        q = input("  Email contains: ").strip()
        print_list(search_by_email(q))
        pause()
    elif ch == "3":
        groups = get_groups()
        for g in groups:
            print(f"    {g['id']}. {g['name']}")
        try:
            gid = int(input("  Group id: ").strip())
        except ValueError:
            return
        sort = pick_sort()
        paginated_browse(group_id=gid, sort_by=sort)

def menu_add():
    header("Add Contact")
    name = input("  Name: ").strip()
    if not name:
        print(c("  Name is required.", RED)); return
    if get_contact_by_name(name):
        print(c(f'  "{name}" already exists.', YEL)); return

    email  = input("  Email: ").strip() or None
    bday   = input("  Birthday YYYY-MM-DD: ").strip() or None
    gid    = pick_group()
    try:
        cid = add_contact_extended(name, email, bday, gid)
        print(c(f'  ✓ Created (id={cid}).', GREEN))
        add_phones_loop(cid)
    except Exception as e:
        print(c(f"  Error: {e}", RED))

def menu_edit():
    header("Edit Contact")
    q = input("  Search name: ").strip()
    results = search_all_fields(q)
    if not results:
        print(c("  Not found.", YEL)); return
    print_list(results)
    try:
        idx = int(input("  Number to edit: ")) - 1
        ct  = results[idx]
    except (ValueError, IndexError):
        print(c("  Invalid.", RED)); return

    full = get_contact_by_id(ct["id"])
    new_name  = input(f"  Name [{full['name']}]: ").strip()        or full["name"]
    new_email = input(f"  Email [{full.get('email') or ''}]: ").strip() or full.get("email")
    new_bday  = input(f"  Birthday [{full.get('birthday') or ''}]: ").strip() or str(full.get("birthday") or "")
    new_gid   = pick_group()

    update_contact_extended(full["id"], new_name, new_email or None, new_bday or None, new_gid)
    print(c("  ✓ Updated.", GREEN))

    phones = get_phones(full["id"])
    if phones:
        print("\n  Current phones:")
        for i, p in enumerate(phones, 1):
            print(f"    {i}. {p['phone']} ({p['type']})")
        dels = input("  Delete by numbers (comma-sep, blank to skip): ").strip()
        if dels:
            for tok in dels.split(","):
                try:
                    delete_phone(phones[int(tok.strip())-1]["id"])
                except (ValueError, IndexError):
                    pass
    add_phones_loop(full["id"])

class _DateEnc(json.JSONEncoder):
    def default(self, obj):
        return obj.isoformat() if isinstance(obj, date) else super().default(obj)

def menu_export_json():
    header("Export to JSON")
    path = input("  Output file [contacts.json]: ").strip() or "contacts.json"
    all_ct = _fetchall()
    result = []
    for ct in all_ct:
        result.append({
            "name":     ct["name"],
            "email":    ct["email"],
            "birthday": ct["birthday"],
            "group":    ct["group_name"],
            "phones":   [
                {"phone": p["phone"], "type": p["type"]}
                for p in get_phones(ct["id"])
            ],
        })
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, cls=_DateEnc)
    print(c(f"  ✓ {len(result)} contacts saved to {path}", GREEN))
    pause()

def _import_one(rec: dict, on_dup: str) -> str:
    
    name = rec.get("name", "").strip()
    if not name:
        return "error"

    existing = get_contact_by_name(name)
    action   = on_dup

    if existing and on_dup == "ask":
        ans = input(f'  Duplicate "{name}". [s]kip / [o]verwrite? ').strip().lower()
        action = "overwrite" if ans.startswith("o") else "skip"

    gid = get_or_create_group(rec["group"]) if rec.get("group") else None

    if existing:
        if action == "skip":
            return "skipped"
        update_contact_extended(existing["id"], name,
                                rec.get("email"), rec.get("birthday"), gid)
        for p in get_phones(existing["id"]):
            delete_phone(p["id"])
        for ph in rec.get("phones", []):
            db_add_phone(existing["id"], ph["phone"], ph.get("type", "mobile"))
        return "overwritten"
    else:
        cid = add_contact_extended(name, rec.get("email"), rec.get("birthday"), gid)
        for ph in rec.get("phones", []):
            db_add_phone(cid, ph["phone"], ph.get("type", "mobile"))
        return "added"

def menu_import_json():
    header("Import from JSON")
    path = input("  JSON file: ").strip()
    if not path:
        return
    print("  On duplicate: 1=ask  2=skip  3=overwrite")
    mode = {"2": "skip", "3": "overwrite"}.get(input("  > ").strip(), "ask")

    try:
        with open(path, encoding="utf-8") as f:
            records = json.load(f)
    except FileNotFoundError:
        print(c(f"  File not found: {path}", RED)); pause(); return

    stats = {"added": 0, "overwritten": 0, "skipped": 0, "error": 0}
    for rec in records:
        stats[_import_one(rec, mode)] += 1

    print(c(f"\n  added={stats['added']}  overwritten={stats['overwritten']}"
            f"  skipped={stats['skipped']}  errors={stats['error']}", GREEN))
    pause()

def menu_import_csv():
    header("Import from CSV (extended)")
    path = input("  CSV file: ").strip()
    if not path:
        return
    print("  On duplicate: 1=ask  2=skip  3=overwrite")
    mode = {"2": "skip", "3": "overwrite"}.get(input("  > ").strip(), "ask")

    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                print(c("  Empty CSV.", RED)); return

            fieldnames = {fn.strip().lower() for fn in reader.fieldnames}
            if "name" not in fieldnames:
                print(c("  CSV must have a 'name' column.", RED)); return

            stats = {"added": 0, "overwritten": 0, "skipped": 0, "error": 0}
            for row in reader:
                row  = {k.strip().lower(): (v or "").strip() for k, v in row.items()}
                name = row.get("name", "")
                if not name:
                    stats["error"] += 1; continue

                phone  = row.get("phone") or None
                ptype  = row.get("phone_type", "mobile").lower()
                if ptype not in ("home", "work", "mobile"):
                    ptype = "mobile"

                rec = {
                    "name":     name,
                    "email":    row.get("email") or None,
                    "birthday": row.get("birthday") or None,
                    "group":    row.get("group") or None,
                    "phones":   [{"phone": phone, "type": ptype}] if phone else [],
                }
                stats[_import_one(rec, mode)] += 1

    except FileNotFoundError:
        print(c(f"  File not found: {path}", RED)); pause(); return

    print(c(f"\n  added={stats['added']}  overwritten={stats['overwritten']}"
            f"  skipped={stats['skipped']}  errors={stats['error']}", GREEN))
    pause()

def menu_add_phone_proc():
    header("add_phone  (stored procedure)")
    name  = input("  Contact name: ").strip()
    phone = input("  Phone number: ").strip()
    ptype = input("  Type [home/work/mobile]: ").strip().lower()
    try:
        call_add_phone(name, phone, ptype)
        print(c("  ✓ Done.", GREEN))
    except Exception as e:
        print(c(f"  Error: {e}", RED))
    pause()

def menu_move_to_group_proc():
    header("move_to_group  (stored procedure)")
    name  = input("  Contact name: ").strip()
    group = input("  Target group (created if new): ").strip()
    try:
        call_move_to_group(name, group)
        print(c("  ✓ Done.", GREEN))
    except Exception as e:
        print(c(f"  Error: {e}", RED))
    pause()

MENU = f

ACTIONS = {
    "1": lambda: paginated_browse(sort_by=pick_sort()),
    "2": menu_search,
    "3": menu_add,
    "4": menu_edit,
    "5": menu_export_json,
    "6": menu_import_json,
    "7": menu_import_csv,
    "8": menu_add_phone_proc,
    "9": menu_move_to_group_proc,
}

def main():
    while True:
        print(MENU)
        ch = input("  > ").strip()
        if ch == "0":
            print(c("  Bye!", CYAN)); sys.exit(0)
        action = ACTIONS.get(ch)
        if action:
            action()
        else:
            print(c("  Unknown option.", YEL))

if __name__ == "__main__":
    main()
