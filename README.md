# Instructions

## Setup Web Server
1. Create a folder called <code>backend</code>
2. Copy all files from <code>WebServer</code> into <code>backend</code>
3. Enter <code>backend</code> folder
4. Run <code>python3 -m venv</code>
5. Run <code>./bin/pip install flask python-dotenv</code>

## Run Web Server
1. Enter <code>backend</code> folder
2. Run <code>./bin/activate</code>
3. Run <code>python3 backend.py &</code>
4. Run <code>flask run</code>

## Setup Zero Controller
1. Create a folder called <code>env</code>
2. Copy all files from <code>ZeroController</code> into <code>env</code>
3. Enter <code>env</code> folder
4. Run <code>python3 -m venv</code>
5. Run <code>./bin/pip install pyserial</code>

## Run Zero Controller
1. Enter <code>env</code> folder
2. Run <code>./bin/activate</code>
3. Run <code>python3 Controller.py</code>

## Setup Pico Window Unit
1. Open <code>ThreadStep.py</code> with Thonny
2. Save as <code>ThreadStep.py</code> on Pico
3. Open <code>main.py</code> with Thonny
4. Save as <code>main.py</code> on Pico

## Run Pico Window Unit
1. Plug into USB Hub for Zero Controller, but leave switch off
2. Run Zero Controller
3. Turn switches on from left to right window unit