# backend.py
import sqlite3


class Database:
    def __init__(self):
        self.conn = sqlite3.connect('studyplanner.db')
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()

        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS studenti (id INTEGER PRIMARY KEY AUTOINCREMENT, nume TEXT, email TEXT UNIQUE, parola TEXT, rol TEXT DEFAULT 'student')''')

        try:
            cursor.execute("ALTER TABLE studenti ADD COLUMN rol TEXT DEFAULT 'student'")
        except sqlite3.OperationalError:
            pass

        cursor.execute(
            "INSERT OR IGNORE INTO studenti (nume, email, parola, rol) VALUES ('admin', 'admin', 'admin', 'admin')")

        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS discipline (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, denumire TEXT, profesor TEXT, credite INTEGER, evidentiere TEXT, FOREIGN KEY(student_id) REFERENCES studenti(id))''')
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS deadlines (id INTEGER PRIMARY KEY AUTOINCREMENT, disciplina_id INTEGER, titluSarcina TEXT, descriere TEXT, dataLimita TEXT, status TEXT, FOREIGN KEY(disciplina_id) REFERENCES discipline(id))''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS sesiuni_studiu (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            disciplina_id INTEGER, 
            data TEXT, 
            durata_secunde INTEGER, 
            durata_tinta_secunde INTEGER,
            notite TEXT, 
            status TEXT, 
            FOREIGN KEY(disciplina_id) REFERENCES discipline(id))''')

        # --- TABEL NOU PENTRU SETĂRI GLOBALE (ADMIN) ---
        cursor.execute('''CREATE TABLE IF NOT EXISTS setari (cheie TEXT PRIMARY KEY, valoare TEXT)''')
        # Inserăm sugestiile implicite dacă nu există deja
        cursor.execute("INSERT OR IGNORE INTO setari (cheie, valoare) VALUES ('sugestii_timp', '15, 30, 45, 60')")

        self.conn.commit()


class StudentRepo:
    def __init__(self, db):
        self.db = db

    def add_student(self, nume, email, parola):
        try:
            self.db.conn.cursor().execute("INSERT INTO studenti (nume, email, parola) VALUES (?, ?, ?)",
                                          (nume, email, parola))
            self.db.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def find_by_email_and_password(self, email, parola):
        return self.db.conn.cursor().execute("SELECT id, nume, email, parola, rol FROM studenti WHERE email=? AND parola=?",
                                             (email, parola)).fetchone()

    def get_all_students(self):
        return self.db.conn.cursor().execute("SELECT id, nume, email, rol FROM studenti").fetchall()

    def update_student(self, student_id, nume, email, parola):
        try:
            self.db.conn.cursor().execute("UPDATE studenti SET nume=?, email=?, parola=? WHERE id=?",
                                          (nume, email, parola, student_id))
            self.db.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False


class DisciplinaRepo:
    def __init__(self, db): self.db = db

    def add(self, student_id, denumire, profesor, credite, evidentiere):
        self.db.conn.cursor().execute(
            "INSERT INTO discipline (student_id, denumire, profesor, credite, evidentiere) VALUES (?, ?, ?, ?, ?)",
            (student_id, denumire, profesor, credite, evidentiere))
        self.db.conn.commit()

    def get_by_student(self, student_id):
        return self.db.conn.cursor().execute(
            "SELECT id, denumire, profesor, credite, evidentiere FROM discipline WHERE student_id=?",
            (student_id,)).fetchall()

    def delete(self, disc_id):
        self.db.conn.cursor().execute("DELETE FROM discipline WHERE id=?", (disc_id,))
        self.db.conn.cursor().execute("DELETE FROM deadlines WHERE disciplina_id=?", (disc_id,))
        self.db.conn.cursor().execute("DELETE FROM sesiuni_studiu WHERE disciplina_id=?", (disc_id,))
        self.db.conn.commit()

    def update(self, disc_id, denumire, profesor, credite, evidentiere):
        self.db.conn.cursor().execute(
            "UPDATE discipline SET denumire=?, profesor=?, credite=?, evidentiere=? WHERE id=?",
            (denumire, profesor, credite, evidentiere, disc_id))
        self.db.conn.commit()


class DeadlineRepo:
    def __init__(self, db): self.db = db

    def add(self, disciplina_id, titlu, descriere, data, status):
        self.db.conn.cursor().execute(
            "INSERT INTO deadlines (disciplina_id, titluSarcina, descriere, dataLimita, status) VALUES (?, ?, ?, ?, ?)",
            (disciplina_id, titlu, descriere, data, status))
        self.db.conn.commit()

    def get_by_student(self, student_id):
        query = '''SELECT d.id, d.titluSarcina, d.dataLimita, d.descriere, disc.denumire, disc.evidentiere, disc.id, d.status
                   FROM deadlines d JOIN discipline disc ON d.disciplina_id = disc.id WHERE disc.student_id = ?'''
        return self.db.conn.cursor().execute(query, (student_id,)).fetchall()

    def delete(self, dead_id):
        self.db.conn.cursor().execute("DELETE FROM deadlines WHERE id=?", (dead_id,))
        self.db.conn.commit()

    def update(self, dead_id, disciplina_id, titlu, descriere, data):
        self.db.conn.cursor().execute(
            "UPDATE deadlines SET disciplina_id=?, titluSarcina=?, descriere=?, dataLimita=? WHERE id=?",
            (disciplina_id, titlu, descriere, data, dead_id))
        self.db.conn.commit()

    def update_status(self, dead_id, new_status):
        self.db.conn.cursor().execute("UPDATE deadlines SET status=? WHERE id=?", (new_status, dead_id))
        self.db.conn.commit()


class StudySessionRepo:
    def __init__(self, db): self.db = db

    def add(self, disciplina_id, data, durata_secunde, durata_tinta, notite, status):
        self.db.conn.cursor().execute(
            "INSERT INTO sesiuni_studiu (disciplina_id, data, durata_secunde, durata_tinta_secunde, notite, status) VALUES (?, ?, ?, ?, ?, ?)",
            (disciplina_id, data, durata_secunde, durata_tinta, notite, status))
        self.db.conn.commit()

    def get_by_student(self, student_id):
        query = '''SELECT s.id, s.data, s.durata_secunde, s.notite, s.status, disc.denumire, disc.evidentiere, disc.id, s.durata_tinta_secunde
                   FROM sesiuni_studiu s JOIN discipline disc ON s.disciplina_id = disc.id WHERE disc.student_id = ?'''
        return self.db.conn.cursor().execute(query, (student_id,)).fetchall()

    def delete(self, ses_id):
        self.db.conn.cursor().execute("DELETE FROM sesiuni_studiu WHERE id=?", (ses_id,))
        self.db.conn.commit()

    def update(self, ses_id, data_str, total_secunde, status):
        self.db.conn.cursor().execute("UPDATE sesiuni_studiu SET data=?, durata_secunde=?, status=? WHERE id=?",
                                      (data_str, total_secunde, status, ses_id))
        self.db.conn.commit()


# --- BUSINESS LOGIC LAYER (Servicii) ---

class AuthService:
    def __init__(self, student_repo):
        self.repo = student_repo
        self.current_user = None

    def login(self, email, parola):
        user = self.repo.find_by_email_and_password(email, parola)
        if user:
            self.current_user = {"id": user[0], "nume": user[1], "email": user[2], "parola": user[3], "rol": user[4]}
            return True
        return False

    def register(self, nume, email, parola):
        return self.repo.add_student(nume, email, parola)

    def update_account(self, nume, email, parola):
        if self.repo.update_student(self.current_user['id'], nume, email, parola):
            self.current_user['nume'] = nume
            self.current_user['email'] = email
            self.current_user['parola'] = parola
            return True
        return False


class PlannerService:
    def __init__(self, disciplina_repo, deadline_repo, session_repo):
        self.disc_repo = disciplina_repo
        self.dead_repo = deadline_repo
        self.ses_repo = session_repo

    def add_disciplina(self, student_id, denumire, profesor, credite, evidentiere):
        if not denumire: raise ValueError("Denumirea este obligatorie!")
        self.disc_repo.add(student_id, denumire, profesor, int(credite) if credite else 0, evidentiere)

    def get_discipline(self, student_id):
        return self.disc_repo.get_by_student(student_id)

    def delete_disciplina(self, disc_id):
        self.disc_repo.delete(disc_id)

    def update_disciplina(self, disc_id, denumire, profesor, credite, evidentiere):
        if not denumire: raise ValueError("Denumirea este obligatorie!")
        self.disc_repo.update(disc_id, denumire, profesor, int(credite) if credite else 0, evidentiere)

    def add_deadline(self, disciplina_id, titlu, descriere, data):
        if not titlu or not data: raise ValueError("Titlul și data sunt obligatorii!")
        self.dead_repo.add(disciplina_id, titlu, descriere, data, "Nefinalizat")

    def get_deadlines(self, student_id):
        return self.dead_repo.get_by_student(student_id)

    def delete_deadline(self, dead_id):
        self.dead_repo.delete(dead_id)

    def update_deadline(self, dead_id, disciplina_id, titlu, descriere, data):
        if not titlu or not data: raise ValueError("Titlul și data sunt obligatorii!")
        self.dead_repo.update(dead_id, disciplina_id, titlu, descriere, data)

    def mark_deadline_completed(self, dead_id):
        self.dead_repo.update_status(dead_id, "Finalizat")

    def save_study_session(self, disciplina_id, durata_secunde, durata_tinta, notite, status):
        from datetime import datetime
        data_azi = datetime.now().strftime("%d-%m-%Y")
        data_str = f"{data_azi}|{durata_secunde}"
        self.ses_repo.add(disciplina_id, data_str, durata_secunde, durata_tinta, notite, status)

    def resume_study_session(self, ses_id, old_data_str, old_total, extra_secunde, status):
        from datetime import datetime
        data_azi = datetime.now().strftime("%d-%m-%Y")
        if "|" not in old_data_str: old_data_str = f"{old_data_str}|{old_total}"
        new_data_str = f"{old_data_str},{data_azi}|{extra_secunde}"
        new_total = old_total + extra_secunde
        self.ses_repo.update(ses_id, new_data_str, new_total, status)

    def get_study_sessions(self, student_id):
        return self.ses_repo.get_by_student(student_id)

    def delete_session(self, ses_id):
        self.ses_repo.delete(ses_id)

    def get_statistics_data(self, student_id):
        import datetime

        sessions = self.get_study_sessions(student_id)
        discipline_time = {}
        daily_time = {}
        total_seconds = 0

        for s in sessions:
            sec = s[2] if s[2] else 0
            mat = s[5]
            date_str = str(s[1])

            total_seconds += sec
            discipline_time[mat] = discipline_time.get(mat, 0) + (sec / 60.0)

            if "," in date_str or "|" in date_str:
                dates = [p.split('|')[0].strip() for p in date_str.split(',')]
                last_date = dates[-1]
            else:
                last_date = date_str

            daily_time[last_date] = daily_time.get(last_date, 0) + (sec / 60.0)

        deadlines = self.get_deadlines(student_id)
        deadlines_status = {"Urmează": 0, "Finalizate": 0, "Depășite": 0}

        for d in deadlines:
            status = d[7]
            data_limita = d[2]
            if status == "Finalizat":
                deadlines_status["Finalizate"] += 1
            else:
                try:
                    dt = datetime.datetime.strptime(data_limita, "%d-%m-%Y").date()
                    if dt < datetime.date.today():
                        deadlines_status["Depășite"] += 1
                    else:
                        deadlines_status["Urmează"] += 1
                except:
                    deadlines_status["Urmează"] += 1

        return {
            "total_minute": total_seconds / 60.0,
            "discipline_time": discipline_time,
            "daily_time": daily_time,
            "deadlines_status": deadlines_status
        }

    # --- METODE NOI PENTRU ADMIN (Setări) ---

    def get_sugestii_timp(self):
        # Ne folosim de conexiunea existentă în orice repository (ex: disc_repo)
        cursor = self.disc_repo.db.conn.cursor()
        res = cursor.execute("SELECT valoare FROM setari WHERE cheie='sugestii_timp'").fetchone()
        if res and res[0]:
            try:
                return [int(x.strip()) for x in res[0].split(',')]
            except:
                return [15, 30, 45, 60]
        return [15, 30, 45, 60]

    def update_sugestii_timp(self, text_valori):
        cursor = self.disc_repo.db.conn.cursor()
        cursor.execute("UPDATE setari SET valoare=? WHERE cheie='sugestii_timp'", (text_valori,))
        self.disc_repo.db.conn.commit()