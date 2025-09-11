import json
from datetime import datetime
from rich.style import Style
from textual import log
from textual.coordinate import Coordinate
from textual.app import App, ComposeResult
from textual.screen import Screen, ModalScreen
from textual.containers import Grid, Horizontal, Vertical
from textual.widgets import DataTable, Footer, Header, Label, Input, Checkbox, Button, Log
from Profisee import Restful


class SettingsDialog(ModalScreen[bool]):
    # def __init__(self, profisee_url: str, client_id: str, verify_ssl: bool) -> None:
    #     self.ProfiseeUrl = profisee_url
    #     self.ClientId = client_id
    #     self.VerifySSL = verify_ssl

    DEFAULT_CSS = """
        SettingsDialog {
            align: center middle;
        }
        
        #settings_dialog {
            width: 80;
            height: 16;
        }
    """

    def compose(self) -> ComposeResult:
        # yield Grid(
        with Vertical(id="settings_dialog"):
            yield Label("Profisee Url:", id="profisee_url_label")
            yield Input(placeholder="Profisee Url", value=self.ProfiseeUrl, id="profisee_url")
            yield Label("Client Id:")
            yield Input(placeholder="Client Id", value=self.ClientId, id="client_id")
            yield Checkbox(label="Verify SSL", value=self.VerifySSL, id="verify_ssl")
            yield Horizontal(Button("Ok", id="ok", variant="success"), Button("Cancel", id="cancel", variant="error"))
                # id="settings_dialog"
        # )
        

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "ok":
                self.ProfiseeUrl = self.query_one("#profisee_url").value
                self.ClientId = self.query_one("#client_id").value
                self.VerifySSL = self.query_one("#verify_ssl").value
                self.dismiss(True)
            case "cancel":
                self.dismiss(False)


class EventLogViewer(App):
    BINDINGS = [
        ("c", "connect", "connect"),
        ("r", "refresh", "refresh"),
        ("q", "quit", "quit")
    ]

    def __init__(self, profisee_url:str = None, client_id:str = None, verify_ssl: bool = True) -> None:
        super().__init__()
        self.api = Restful.API(profisee_url, client_id, verify=verify_ssl)
        
    def compose(self):
        yield Header(show_clock=True)
        yield DataTable(id="data_table", zebra_stripes=True)
        yield Footer()
                
    def on_mount(self) -> None:
        self.title = "Profisee Event Log Viewer"
        self.sub_title = f"API({self.api.ProfiseeUrl}, {self.api.ClientId}, {self.api.VerifySSL})"
        
        self.load_log_events()
        self.set_interval(15, self.load_log_events)

        self.log(f"API({self.api.ProfiseeUrl}, {self.api.ClientId}, {self.api.VerifySSL})")
        log(f"EventLogViewer initialized at {datetime.now().isoformat()}")
        log(locals())

    def load_log_events(self) -> None:
        self.log("Loading log events...")
        log_event_list = []        
        try:
            log_events = self.api.GetLogEvents(pageSize=50)

            for log_event in log_events:
                log_event_list.append((
                    log_event.get("timeStamp", ""),
                    log_event.get("level", ""),
                    log_event.get("id", ""), 
                    log_event.get("message", "")) 
                )
        except Exception as ex:
            print(f"Failed to load log events: {ex}")
            # self.log_message("ERROR", f"Failed to load log events: {ex}")

        data_table = self.query_one(DataTable)
        data_table.columns.clear()
        data_table.add_columns("Timestamp", "Level", "ID", "Message")
        data_table.rows.clear()
        data_table.add_rows(log_event_list)
        
        result_cells = data_table.get_column_at(1)
        for row_number, result in enumerate(result_cells):
            match result:
                case "Debug": color = "cyan"
                case "Info": color = "green"
                case "Warning": color = "yellow"
                case "Error": color = "red"
                case _: color = "white"

            for column_number in range(0, len(data_table.columns)):
                cell_coordinate = Coordinate(row_number, column_number)
                value = data_table.get_cell_at(cell_coordinate)
                data_table.update_cell_at(cell_coordinate, f"[{color}]{value}[/{color}]")

    async def action_refresh(self) -> None:
        self.load_log_events()
        
    async def action_connect(self):
        self.settings_dialog = SettingsDialog() # self.api.ProfiseeUrl, self.api.ClientId, self.api.VerifySSL)
        self.settings_dialog.ProfiseeUrl = self.api.ProfiseeUrl
        self.settings_dialog.ClientId = self.api.ClientId
        self.settings_dialog.VerifySSL = self.api.VerifySSL

        self.push_screen(self.settings_dialog, self.settings_updated)

    def settings_updated(self, updated: bool) -> None:
        print(f"Settings updated: {updated}")
        if updated:
            self.api = Restful.API(self.settings_dialog.ProfiseeUrl, self.settings_dialog.ClientId, verify=self.settings_dialog.VerifySSL)        
            self.sub_title = f"API({self.api.ProfiseeUrl}, {self.api.ClientId}, {self.api.VerifySSL})"

if __name__ == "__main__":
    instance_name = "Local"
    settings = json.load(open(r"settings.json"))[instance_name]
    profisee_url = settings.get("ProfiseeUrl", None)
    client_id = settings.get("ClientId", None)
    verify_ssl = settings.get("VerifySSL", True)    
    EventLogViewer(profisee_url, client_id, verify_ssl).run()
