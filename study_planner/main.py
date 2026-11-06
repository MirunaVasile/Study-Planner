# main.py
import tkinter as tk
from config import C_DARK_PURPLE
from backend import Database, StudentRepo, DisciplinaRepo, DeadlineRepo, AuthService, PlannerService

from login_page import LoginFrame
from register_page import RegisterFrame
from dashboard_page import MainAppFrame


class StudyPlannerApp:
    def __init__(self, root, auth_service, planner_service):
        self.root = root
        self.root.title("Study Planner")
        self.root.geometry("850x600")
        self.root.configure(bg=C_DARK_PURPLE)

        self.auth_service = auth_service
        self.planner_service = planner_service

        self.container = tk.Frame(self.root, bg=C_DARK_PURPLE)
        self.container.pack(fill="both", expand=True)

        self.frames = {}

        for F in (LoginFrame, RegisterFrame, MainAppFrame):
            frame = F(self.container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.show_frame("LoginFrame")

    def show_frame(self, frame_name):
        frame = self.frames[frame_name]
        frame.tkraise()
        if frame_name == "MainAppFrame":
            frame.load_dashboard()


if __name__ == "__main__":
    from backend import StudySessionRepo

    db = Database()

    auth_srv = AuthService(StudentRepo(db))
    plan_srv = PlannerService(DisciplinaRepo(db), DeadlineRepo(db), StudySessionRepo(db))

    root = tk.Tk()
    app = StudyPlannerApp(root, auth_srv, plan_srv)
    root.mainloop()