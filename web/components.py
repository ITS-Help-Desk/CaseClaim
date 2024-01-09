from enum import Enum

"""
NOTE: HEAVILY USES BOOTSTRAP -- Use bootstrap componenets to render pieces of the gui for our bot.

@TODO: Make it classy so that the indentation is nice on client side :skull:
"""

class SidebarOptions(Enum):
    """
    Enum to represent sidebar options with less ambiguity
    """
    DASHBOARD  = 1
    STATISTICS = 2

class StatsType(Enum):
    """
    Enum to represent what the type of stats object is being requested
    """
    IMAGE = 1
    TEXT = 2 # Not implemented yet

def nav_column(active: SidebarOptions, bot_running: bool, token: bool) -> str:
    """
    Generate a reusable sidebar for html templating.

    Args:
        active          The active page
        bot_running     True if the bot is running false otherwise
        token           True of the token is saved false otherwise

    Returns:
        A sidebar html component as a string
    """

    DASHBOARD_REL_PATH = "/"
    STATISTICS_REL_PATH = "/stats"
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
    nav_column += "</ul>"
    nav_column += status_panel
    nav_column += """
        </div>
    </div>
    """

    return nav_column

def card(description: str, title: str, additional_elements: list[str] | str = "") -> str:
    """
    Generate a card component as a string.

    Args:
        description             The card description
        title                   The card title
        additional_elements     Any additional html elements to insert into the card-body

    Returns:
        card html component as a string`
    """
    # h-100 because I want the cards to be equal heights
    card_str = f"""
    <div class="card h-100">
        <div class="card-body">
            <h5 class="card-title">{title}</h5>
            <p class="card-text">{description}</p>
            {additional_elements}
        </div>
    </div>
    """
    return card_str

def button(style: str, text: str, alt_tag:str | None = None, additional_meta: str = "") -> str:
    """
    Return an html component stylized as a button.

    Args:
        style                   The button class (and any other class names)
        text                    The text for the button
        alt_tag                 The specific html tag to use (Do not include angle braces)
        additional_meta         Any additional meta tags for the button 

    Return:
        Button stylized component as a string
    """
    if alt_tag == None:
        return f"""<button class="btn {style}" {additional_meta}>{text}</button>"""
    elif alt_tag == "input":
        return f"""<input class="btn {style}" {additional_meta}>"""
    else:
        return f"""<{alt_tag} class="btn {style}" {additional_meta}>{text}</{alt_tag}>"""

def stats_box(stype: StatsType, path="/leadstats.png", data="") -> str:
    """
    Generate the requested statistic for display. If the stype is IMAGE, path is the path to the image and data
    is the alt text. If stype is TEXT, path is unused and data is the html component to use.

    @TODO: Implement text stats such as leaderboards, logs, etc

    Args:
        stype   The type of statistic: StatsType.IMAGE or StatsType.TEXT
        path    The path to the image
        data    The text component to add or alt text for an image.

    Return:
        An html component for the requested statistic as a str
    """
    if stype == StatsType.IMAGE:
        return f'<img class="img-fluid" alt="{data}" src="{path}">'
    elif stype == StatsType.TEXT:
        return "Not Implmented Yet"
    else:
        return f'<img class="img-fluid" alt="{data}" src="/leadstats/month">'

def col_wrap(internal_components: str) -> str:
    """
    Self explanatory
    """
    return f'<div class="col">{internal_components}</div>'

def stats_controls() -> str:
    """
    Generate a grid of cards that control which statistic is generated.

    @TODO: Allow parameter selection

    Return:
        A card grid html component for stats buttons
    """
    ctrls = '<div class="row row-cols-4 row-cols-md-4 justify-content-start no-gutters">'

    leadstat_buttons = '<div class="row row-cols-2 row-cols-sm-1 row-cols-md-2 row-cols-lg-2 justify-content-start no-gutters">'
    leadstat_buttons += col_wrap(button("btn-primary", "Month", alt_tag="a", additional_meta='href="/stats/leadstats/month"'))
    leadstat_buttons += col_wrap(button("btn-primary", "Semester", alt_tag="a", additional_meta='href="/stats/leadstats/semester"'))
    leadstat_buttons += "</div>"
    ctrls += col_wrap(card("Generate lead statistics", "Lead Statistics", leadstat_buttons)) 
    ctrls += col_wrap(card("Generate case distribtuion for today.", "Case Distribution",
                           button("btn-primary", "Graph", alt_tag="a", additional_meta='href="/stats/casedist"')))
    ctrls += '</div>'
    return ctrls
    

def bot_controls(need_token: bool) -> str:
    """
    Generate cards to control the bot.

    @TODO: Implement IPC with bot to do bot commands

    Args:
        need_token  True if the token is not saved, false otherwise

    Return:
        A card grid html component for bot controls.
    """
    ctrls = '<div class="row row-cols-2 row-cols-md-1 justify-content-start no-gutters">'
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
        ctrls += col_wrap(card("We do not have a bot token saved. Please enter it here and save it.",
                      "Save Token",
                      token_form
                      ))
    else:
        ctrls += col_wrap(card("Starts the bot.",
                      "Start Bot", 
                      button("btn-primary", "Start", alt_tag="a", additional_meta='href="/start_bot"')))
        ctrls += col_wrap(card("Stops the bot.",
                      "Stop Bot",
                      button("btn-danger", "Stop", alt_tag="a", additional_meta='href="/stop_bot"')
                      ))
    ctrls += "</div>"
    return ctrls

def login_controls(signed_in: bool) -> str:
    if signed_in:
        return '<a href="/logout" class="nav-link">Sign Out</a>'
    else:
        return '<a href="/login" class="nav-link">Sign In </a>'

def alert(message: str, level: str) -> str:
    return f'<div class="alert alert-{level}" role="alert">{message}</div>'
