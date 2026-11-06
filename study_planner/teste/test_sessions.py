import unittest
import sqlite3
from backend import Database, StudentRepo, DisciplinaRepo, DeadlineRepo, StudySessionRepo, PlannerService


class TestStudySessions(unittest.TestCase):
    def setUp(self):
        """Pregătim baza de date, un student și o materie de care să legăm sesiunile."""
        self.db = Database()
        self.db.conn = sqlite3.connect(':memory:')
        self.db.create_tables()

        self.student_repo = StudentRepo(self.db)
        self.planner_service = PlannerService(
            DisciplinaRepo(self.db),
            DeadlineRepo(self.db),
            StudySessionRepo(self.db)
        )

        # 1. Creăm studentul
        self.student_repo.add_student("Student Sesiuni", "sesiuni@test.ro", "123")
        self.student_id = self.student_repo.find_by_email_and_password("sesiuni@test.ro", "123")[0]

        # 2. Creăm materia
        self.planner_service.add_disciplina(self.student_id, "Sisteme de Operare", "Prof. Z", 5, "#a8c8f5")
        self.disc_id = self.planner_service.get_discipline(self.student_id)[0][0]

    def test_salvare_sesiune_noua(self):
        """Test: Crearea unei sesiuni de studiu (CREATE)."""
        # Salvăm o sesiune de 2 ore (7200 secunde)
        self.planner_service.save_study_session(self.disc_id, 7200, 7200, "Citit curs 1-3", "Finalizat")

        sesiuni = self.planner_service.get_study_sessions(self.student_id)
        self.assertEqual(len(sesiuni), 1)

        # Verificăm datele sesiunii (index 2 e durata_secunde, 3 e notițele)
        self.assertEqual(sesiuni[0][2], 7200)
        self.assertEqual(sesiuni[0][3], "Citit curs 1-3")
        self.assertEqual(sesiuni[0][4], "Finalizat")

    def test_reluare_sesiune_studiu(self):
        """Test: Reluarea unei sesiuni și adunarea timpului (UPDATE)."""
        # 1. Creăm o sesiune inițială amânată (Nefinalizat), 30 min (1800 sec)
        self.planner_service.save_study_session(self.disc_id, 1800, 3600, "Pauza de masa", "Nefinalizat")
        sesiune_initiala = self.planner_service.get_study_sessions(self.student_id)[0]

        ses_id = sesiune_initiala[0]
        data_str_initiala = sesiune_initiala[1]

        # 2. Reluăm sesiunea și adăugăm încă 30 min (1800 sec), apoi o finalizăm
        self.planner_service.resume_study_session(ses_id, data_str_initiala, 1800, 1800, "Finalizat")

        # 3. Verificăm dacă timpul s-a adunat corect (1800 + 1800 = 3600 secunde)
        sesiune_updatata = self.planner_service.get_study_sessions(self.student_id)[0]
        self.assertEqual(sesiune_updatata[2], 3600, "Timpul total nu a fost calculat corect la reluare!")
        self.assertEqual(sesiune_updatata[4], "Finalizat", "Statusul nu s-a actualizat corect.")

    def test_stergere_sesiune(self):
        """Test: Ștergerea unei sesiuni (DELETE)."""
        self.planner_service.save_study_session(self.disc_id, 600, 600, "Scurta", "Finalizat")
        ses_id = self.planner_service.get_study_sessions(self.student_id)[0][0]

        self.planner_service.delete_session(ses_id)

        sesiuni = self.planner_service.get_study_sessions(self.student_id)
        self.assertEqual(len(sesiuni), 0)

    def tearDown(self):
        self.db.conn.close()