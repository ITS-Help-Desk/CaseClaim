from enum import Enum

"""
Use bootstrap componenets to render pieces of the gui for our bot.
"""

class SidebarOptions(Enum):
    """
    Enum to represent sidebar options with less ambiguity
    """
    DASHBOARD  = 1
    STATISTICS = 2

def nav_column(active: SidebarOptions, bot_running: bool, token: bool) -> str:
    DASHBOARD_REL_PATH = "/index.html"
    STATISTICS_REL_PATH = "/stats"
    CSS_WIKI_LINK = "#" # Idk if this is a public link or not so redacted for now
    GITHUB_LINK = "https://github.com/ajockelle/CaseClaim"
    dashboard=f"""
    <li class="nav-item">
        <a href="{DASHBOARD_REL_PATH}" class="nav-link d-flex align-items-center gap-2{" active" if active == SidebarOptions.DASHBOARD else ""}">
            <span data-feather="server"></span>
            Dashboard
            </a>
    </li>"""
    
    statistics=f"""
    <li class="nav-item">
        <a href="{STATISTICS_REL_PATH}" class="nav-link d-flex align-items-center gap-2{" active" if active == SidebarOptions.STATISTICS else ""}">
            <span data-feather="bar-chart"></span>
            Statistics 
            </a>
    </li>"""
    github=f"""
    <li class="nav-item">
        <a href="{GITHUB_LINK}" class="nav-link d-flex align-items-center gap-2" target="_blank">
            <span data-feather="github"></span>
            Github
        </a>
    </li>
    """
    css_wiki = f"""
    <li class="nav-item">
        <a href="{CSS_WIKI_LINK}" class="nav-link d-flex align-items-center gap-2" target="_blank">
            <span data-feather="help-circle"></span>
            CSS Wiki
        </a>
    </li>
    """
    status_panel = f"""
        <h6 class="sidebar-heading d-flex justify-content-between align-items-center px-3 mt-4 mb-1 text-body-secondary text-uppercase">
            <span>Bot Status</span>
        </h6>
        <ul class="nav flex-column mb-auto">
            <li class="nav-item">
                <div class="nav-link d-flex align-items-center gap-2">
                    <span data-feather="power"></span>
                    Bot: <span class="badge rounded-pill bg-{"success" if bot_running else "danger"}">{"Running" if bot_running else "Stopped"}</span>
                </div>
            </li>
            <li class="nav-item">
                <div class="nav-link d-flex align-items-center gap-2">
                    <span data-feather="key"></span>
                    Token: <span class="badge rounded-pill bg-{"success" if token else "warning text-dark"}">{"Found" if token else  "Not Found"}</span>
                <div class="nav-link d-flex align-items-center gap-2">
            </li>
        </ul>
    """ 
    nav_column = """
    <div class="sidebar col-md-3 col-lg-2 p-0 bg-body-tertiary">
        <div class="offcanvas-md offcanvas-end bg-body-tertiary" tabindex="-1" id="sidebarMenu">
            <ul class="nav flex-column">"""
    nav_column += dashboard
    nav_column += statistics
    nav_column += github
    nav_column += css_wiki
    nav_column += "</ul>"
    nav_column += status_panel
    nav_column += """
        </div>
    </div>
    """
    return nav_column

def card(description: str, title: str, additional_elements:str = "") -> str:
    return f"""
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">{title}</h5>
            <p class="card-text">{description}</p>
            {additional_elements}
        </div>
    </div>
    """
def button(style: str, text: str, alt_tag:str | None = None, additional_meta: str = "") -> str:
    if alt_tag == None:
        return f"""<button class="btn {style}" {additional_meta}>{text}</button>"""
    elif alt_tag == "input":
        return f"""<input class="btn {style}" {additional_meta}>"""
    else:
        return f"""<{alt_tag} class="btn {style}" {additional_meta}>{text}</{alt_tag}>"""

def bot_controls(need_token: bool) -> str:
    ctrls = '<div class="row row-cols-2 row-cols-md-2 justify-content-start no-gutters">'
    if need_token:
        token_form = """
        <form action="/token" method="post">
            <div class="form-group">
                <label for="token">Enter your Discord bot token:</label>
                <input type="text" value="e.g. MTA123..." id="token" name="token" required>
            </div>
        """
        token_form += button("btn-primary", "Save", additional_meta='type="submit"') + "</div>"
        token_form += "</form>"
        ctrls += '<div class="col">' + card("We do not have a bot token saved. Please enter it here and save it.",
                      "Save Token",
                      token_form
                      ) + '</div>'
    else:
        ctrls += '<div class="col">' + card("Starts the bot.",
                      "Start Bot", 
                      button("btn-primary", "Start", alt_tag="a", additional_meta='href="/start_bot"')) + "</div>"
        ctrls += '<div class="col">' + card("Stops the bot.",
                      "Stop Bot",
                      button("btn-danger", "Stop", alt_tag="a", additional_meta='href="/stop_bot"')
                      ) + "</div>"
    ctrls += "</div>"
    return ctrls

