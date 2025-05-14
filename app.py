from shiny import App, reactive, render, ui
import subprocess
import sys
import io
import contextlib
import traceback

app_ui = ui.page_fluid(
    ui.h1("Python Shell"),
    ui.p("Execute Python code directly in your application."),
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_text_area(
                "code", 
                "Enter Python code:", 
                value="print('Hello, world!')\nx = 5\nprint(f'x squared is {x**2}')",
                height="200px", 
                width="100%",
                placeholder="# Enter Python code here..."
            ),
            ui.input_action_button("run", "Run Code", class_="btn-primary"),
            ui.hr(),
            ui.input_switch("show_exec_info", "Show execution info", value=True),
            ui.p("Note: This executes real Python code. Be careful with what you run."),
            width="350px"
        ),
        ui.card(
            ui.card_header("Output"),
            ui.output_ui("exec_info"),
            ui.hr(),
            ui.output_text("code_output"),
        )
    )
)

def server(input, output, session):
    
    @render.ui
    def exec_info():
        if input.show_exec_info():
            return ui.div(
                ui.p(f"Python version: {sys.version}", 
                    style="color: #666; font-style: italic;"),
                ui.p(f"Executable: {sys.executable}", 
                    style="color: #666; font-style: italic;")
            )
        return ui.div()
    
    @render.text
    def code_output():
        # Return empty string if button not yet clicked
        if not input.run():
            return "Output will appear here after running code."
        
        # Get the Python code to execute
        code = input.code()
        if not code.strip():
            return "Please enter some Python code."
        
        # Capture output using stringIO
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        try:
            # Execute the code and capture stdout/stderr
            with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
                # Execute in the current scope
                exec(code)
            
            # Get the captured output
            stdout = stdout_capture.getvalue()
            stderr = stderr_capture.getvalue()
            
            # Format the response
            output_text = ""
            if stdout:
                output_text += "--- STDOUT ---\n"
                output_text += stdout + "\n"
            
            if stderr:
                output_text += "--- STDERR ---\n"
                output_text += stderr
                
            if not stdout and not stderr:
                output_text = "Code executed successfully with no output."
                
            return output_text
            
        except Exception as e:
            # Capture the full traceback
            tb = traceback.format_exc()
            return f"Error executing code:\n\n{tb}"
        
        finally:
            # Close the StringIO objects
            stdout_capture.close()
            stderr_capture.close()
    
    # Register outputs
    output.exec_info = exec_info
    output.code_output = code_output

app = App(app_ui, server)
