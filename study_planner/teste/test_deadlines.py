import unittest
import sqlite3
from backend import Database, StudentRepo, DisciplinaRepo, DeadlineRepo, StudySessionRepo, PlannerService


class TestDeadlines(unittest.TestCase):
    def setUp(self):
        """Pregătim mediul: baza de date, un student și o materie de test."""
        self.db = Database()
        self.db.conn = sqlite3.connect(':memory:')
        self.db.create_tables()

        self.student_repo = StudentRepo(self.db)
        self.planner_service = PlannerService(
            DisciplinaRepo(self.db),
            DeadlineRepo(self.db),
            StudySessionRepo(self.db)
        )

        self.student_repo.add_student("Student", "test@test.ro", "123")
        self.student_id = self.student_repo.find_by_email_and_password("test@test.ro", "123")[0]

        self.planner_service.add_disciplina(self.student_id, "Fizica", "Prof. Pop", 5, "#a8c8f5")
        self.disc_id = self.planner_service.get_discipline(self.student_id)[0][0]

    def test_adaugare_deadline_succes(self):
        """Test: Crearea unui deadline valid."""
        self.planner_service.add_deadline(self.disc_id, "Proiect Laborator", "Referat 5 pagini", "15-05-2024")

        deadlines = self.planner_service.get_deadlines(self.student_id)
        self.assertEqual(len(deadlines), 1)
        self.assertEqual(deadlines[0][1], "Proiect Laborator")  # Verificăm titlul
        self.assertEqual(deadlines[0][7], "Nefinalizat")  # Statusul implicit trebuie să fie Nefinalizat

    def test_adaugare_deadline_fara_titlu_esueaza(self):
        """Test: Validarea datelor (Titlul și data sunt obligatorii)."""
        with self.assertRaises(ValueError):
            self.planner_service.add_deadline(self.disc_id, "", "Info", "15-05-2024")

    def test_editare_deadline(self):
        """Test: Modificarea unui deadline existent."""
        self.planner_service.add_deadline(self.disc_id, "Tema 1", "Ex. 1", "20-05-2024")
        dead_id = self.planner_service.get_deadlines(self.student_id)[0][0]

        self.planner_service.update_deadline(dead_id, self.disc_id, "Tema 1 Corectata", "Ex. 1-3", "22-05-2024")

        deadlines_upd = self.planner_service.get_deadlines(self.student_id)
        self.assertEqual(deadlines_upd[0][1], "Tema 1 Corectata")
        self.assertEqual(deadlines_upd[0][3], "Ex. 1-3")

    def test_marcare_finalizat(self):
        """Test: Schimbarea statusului în 'Finalizat'."""
        self.planner_service.add_deadline(self.disc_id, "Examen", "Sala 201", "30-05-2024")
        dead_id = self.planner_service.get_deadlines(self.student_id)[0][0]

        self.planner_service.mark_deadline_completed(dead_id)

        deadlines = self.planner_service.get_deadlines(self.student_id)
        self.assertEqual(deadlines[0][7], "Finalizat")

    def test_stergere_deadline(self):
        """Test: Ștergerea unui deadline."""
        self.planner_service.add_deadline(self.disc_id, "De sters", "-", "10-10-2024")
        dead_id = self.planner_service.get_deadlines(self.student_id)[0][0]

        self.planner_service.delete_deadline(dead_id)

        deadlines = self.planner_service.get_deadlines(self.student_id)
        self.assertEqual(len(deadlines), 0)

    def tearDown(self):
        self.db.conn.close()