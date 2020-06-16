# Welcome to the "Integrating physical devices with IOTA - The Track&Trace App." tutorial.

In this tutorial we are creating a simple web App. that simulates using the IOTA tangle as a global DLT to record events in a typical supply chain.

You will find the full tutorial with text and images here

Warning!!
The Track&Trace App. is a server-side web App. built on top of the [Flask web framework](https://flask.palletsprojects.com/en/1.1.x/), and should be run inside a Linux environment (the code will not run correctly inside a native Windows environment)

In case you do not have access to a Linux system, I suggest you install and run the App. inside a [Windows WSL environment](https://docs.microsoft.com/en-us/windows/wsl/).

### Getting started

Python 3 and `pip` are required to run these examples. It is highly recommended to run these examples in a own Python virtual environment.

You can install and run a functional version of the App. using the following procedure:

```
git clone https://github.com/huggre/trackntrace
cd trackntrace
pip install -r requirements.txt
python app.py
```

#### Contribution

PRs are welcome on `master`