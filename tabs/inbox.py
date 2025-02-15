import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from utils.email import *

class Inbox(ctk.CTkFrame):
    def __init__(self, parent, session, manager_id):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 700, corner_radius = 0)

        self.parent = parent
        self.session = session
        self.manager_id = manager_id

        self.team = Teams.get_teams_by_manager(self.session, self.manager_id)[0]
        self.leagueTeams = LeagueTeams.get_league_by_team(self.session, self.team.id)
        self.league = League.get_league_by_id(self.session, self.leagueTeams.league_id)

        self.emailsFrame = ctk.CTkScrollableFrame(self, width = 280, height = 645, fg_color = TKINTER_BACKGROUND, corner_radius = 0)
        self.emailsFrame.place(x = 0, y = 55, anchor = "nw")

        self.titleFrame = ctk.CTkFrame(self, width = 300, height = 50, fg_color = TKINTER_BACKGROUND, corner_radius = 0)
        self.titleFrame.place(x = 0, y = 0, anchor = "nw")

        ctk.CTkLabel(self.titleFrame, text = "Emails", font = (APP_FONT_BOLD, 30), fg_color = TKINTER_BACKGROUND).place(relx = 0.5, rely = 0.5, anchor = "center")

        self.emailDataFrame = ctk.CTkFrame(self, width = 700, height = 700, fg_color = TKINTER_BACKGROUND, corner_radius = 0)
        self.emailDataFrame.place(x = 300, y = 0, anchor = "nw")
        
        canvas = ctk.CTkCanvas(self, width = 5, height = 1000, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(x = 370, rely = 0.5, anchor = "w")

        canvas = ctk.CTkCanvas(self, width = 370, height = 5, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(x = 0, y = 65, anchor = "w")

        self.importEmails()

    def importEmails(self):
        emails = Emails.get_all_emails(self.session)

        if not emails:
            self.addEmail("matchday_preview", matchday = 1)
            self.addEmail("welcome")
            self.saveEmail("welcome")
            self.saveEmail("matchday_preview", matchday = 1)

            return

        email_operations = [
            {"type": "matchday_preview", "matchday": self.league.current_matchday, "condition": self.league.current_matchday <= 38},
            {"type": "matchday_review", "matchday": self.league.current_matchday - 1, "condition": self.league.current_matchday > 1},
        ]

        # Add emails
        for email in email_operations:
            if not Emails.get_email_by_matchday_and_type(self.session, email["matchday"], email["type"]):
                print("Adding email")
                self.addEmail(email["type"], matchday = email["matchday"])

        # Save emails in reverse order
        for email in reversed(email_operations):
            if not Emails.get_email_by_matchday_and_type(self.session, email["matchday"], email["type"]):
                print("Saving email")
                self.saveEmail(email["type"], matchday = email["matchday"])

        for email in reversed(emails):
            self.addEmail(email.email_type, email.matchday, email.player_id)

    def addEmail(self, email_type, matchday = None, player_id = None, imported = False):
        EmailFrame(self.emailsFrame, self.session, self.manager_id, email_type, matchday, player_id, self.emailDataFrame, self)

    def saveEmail(self, email_type, matchday = None, player_id = None):
        Emails.add_email(self.session, email_type, matchday, player_id)
