import unittest
import sqlite3
from backend import Database, StudentRepo, DisciplinaRepo, DeadlineRepo, StudySessionRepo, PlannerService


class TestDiscipline(unittest.TestCase):
    def setUp(self):
        """Pregătim mediul de testare înainte de FIECARE test."""
        self.db = Database()
        self.db.conn = sqlite3.connect(':memory:')  # Bază de date izolată în RAM
        self.db.create_tables()

        self.student_repo = StudentRepo(self.db)
        self.disc_repo = DisciplinaRepo(self.db)
        self.planner_service = PlannerService(
            self.disc_repo,
            DeadlineRepo(self.db),
            StudySessionRepo(self.db)
        )

        self.student_repo.add_student("Student Test", "test@univ.ro", "parola")
        self.student_id = self.student_repo.find_by_email_and_password("test@univ.ro", "parola")[0]

    def test_adaugare_disciplina_succes(self):
        """Test: Crearea unei materii noi (CREATE)."""
        self.planner_service.add_disciplina(self.student_id, "Programare Web", "Prof. Ionescu", 5, "#cfa8f5")

        discipline = self.planner_service.get_discipline(self.student_id)
        self.assertEqual(len(discipline), 1, "Ar trebui să existe exact o materie salvată.")
        self.assertEqual(discipline[0][1], "Programare Web")
        self.assertEqual(discipline[0][3], 5)

    def test_adaugare_disciplina_fara_nume_esueaza(self):
        """Test: Validarea datelor (Nu permitem materii fără nume)."""
        with self.assertRaises(ValueError) as context:
            self.planner_service.add_disciplina(self.student_id, "", "Prof. Popescu", 4, "#cfa8f5")

        self.assertTrue("Denumirea este obligatorie!" in str(context.exception))

    def test_editare_disciplina(self):
        """Test: Actualizarea datelor unei materii (UPDATE)."""
        self.planner_service.add_disciplina(self.student_id, "Baze de Date", "Prof. X", 4, "#cfa8f5")
        disc_id = self.planner_service.get_discipline(self.student_id)[0][0]

        self.planner_service.update_disciplina(disc_id, "Baze de Date Avansate", "Prof. Y", 6, "#a8c8f5")

        discipline_upd = self.planner_service.get_discipline(self.student_id)
        self.assertEqual(discipline_upd[0][1], "Baze de Date Avansate")
        self.assertEqual(discipline_upd[0][2], "Prof. Y")
        self.assertEqual(discipline_upd[0][3], 6)

    def test_stergere_disciplina(self):
        """Test: Ștergerea unei materii (DELETE)."""
        self.planner_service.add_disciplina(self.student_id, "Matematica", "Prof. Z", 5, "#cfa8f5")
        disc_id = self.planner_service.get_discipline(self.student_id)[0][0]

        self.planner_service.delete_disciplina(disc_id)

        discipline = self.planner_service.get_discipline(self.student_id)
        self.assertEqual(len(discipline), 0, "Materia nu a fost ștearsă corect.")

    def tearDown(self):
        """Închidem conexiunea după fiecare test."""
        self.db.conn.close()