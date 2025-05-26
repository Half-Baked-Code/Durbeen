import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(
    [
        # Sidebar
        html.Div(
            [
                html.H2("StudyBot", className="sidebar-header"),
                html.Div(
                    [
                        html.Div("Chat", className="sidebar-item active"),
                        html.Div("Course Materials", className="sidebar-item"),
                        html.Div("Study Guides", className="sidebar-item"),
                        html.Div("Account", className="sidebar-item"),
                    ],
                    className="sidebar-menu",
                ),
                html.Div("Help and Docs", className="sidebar-footer"),
            ],
            className="sidebar",
        ),
        # Main chat area
        html.Div(
            [
                html.H2("Chat", className="chat-header"),
                html.Div(
                    [
                        # Bot message
                        html.Div(
                            [
                                html.Img(
                                    src="/assets/bot-icon.png", className="avatar"
                                ),
                                html.Div(
                                    "Hi there! I’m StudyBot, your AI study assistant. How can I help you today?",
                                    className="bot-message",
                                ),
                            ],
                            className="message-row",
                        ),
                        # User message
                        html.Div(
                            [
                                html.Div(
                                    "Hi StudyBot, I need help with my calculus homework.",
                                    className="user-message",
                                ),
                                html.Img(
                                    src="/assets/user-icon.png", className="avatar"
                                ),
                            ],
                            className="message-row user",
                        ),
                    ],
                    className="chat-history",
                ),
                # Input bar
                html.Div(
                    [
                        dcc.Input(
                            placeholder="Ask StudyBot anything...",
                            className="chat-input",
                            type="text",
                        ),
                        html.Button("Send", className="send-button"),
                    ],
                    className="chat-input-row",
                ),
            ],
            className="main",
        ),
    ],
    className="container",
)

if __name__ == "__main__":
    app.run(debug=True)
