import subprocess
import sys
import os
import time
import signal

def start_backend():
    print("Starting Backend (FastAPI) on port 8000...")
    # Using sys.executable to ensure we use the same python environment
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--reload", "--port", "8000"],
        cwd=os.getcwd()
    )

def start_frontend():
    print("Starting Frontend (Vite) on port 5173...")
    # Check if node_modules exists
    if not os.path.exists(os.path.join("frontend", "node_modules")):
        print("Installing frontend dependencies...")
        subprocess.run(["npm", "install"], cwd="frontend")
    
    return subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=os.path.join(os.getcwd(), "frontend"),
        shell=True if os.name == 'nt' else False
    )

def main():
    backend_proc = None
    frontend_proc = None
    
    try:
        backend_proc = start_backend()
        frontend_proc = start_frontend()
        
        print("\nHybrid Search AI is running!")
        print("API: http://localhost:8000")
        print("UI:  http://localhost:5173")
        print("\nPress Ctrl+C to stop both servers.")
        
        while True:
            time.sleep(1)
            if backend_proc.poll() is not None:
                print("Backend process died. Exiting.")
                break
            if frontend_proc.poll() is not None:
                print("Frontend process died. Exiting.")
                break
                
    except KeyboardInterrupt:
        print("\nStopping servers...")
    finally:
        if backend_proc:
            backend_proc.terminate()
        if frontend_proc:
            if os.name == 'nt':
                # On Windows, terminating shell=True processes is tricky
                subprocess.run(['taskkill', '/F', '/T', '/PID', str(frontend_proc.pid)], capture_output=True)
            else:
                frontend_proc.terminate()
        print("Goodbye!")

if __name__ == "__main__":
    main()
