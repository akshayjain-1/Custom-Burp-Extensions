import re
import socket
import threading
from burp import IBurpExtender, ITab
from javax import swing
from java.awt import BorderLayout
import sys, time, socket
from exceptions_fix import FixBurpExceptions

# Code to load the tab in the Burp Suite app
class BurpExtender(IBurpExtender, ITab):
    def registerExtenderCallbacks(self, callbacks):
        self.clicked = False
        self.response_data = None
        self.kill_thread = False
        
        sys.stdout = callbacks.getStdout()
        
        self.callbacks = callbacks
        
        self.callbacks.setExtensionName("Unencrypted Bind Shell")
        
        self.tab = swing. JPanel(BorderLayout())
        
        # Manager the visual layout with the custom extension tab
        text_panel = swing.JPanel()
        box_vertical = swing.Box.createVerticalBox()
        
        box_horizontal = swing.Box.createHorizontalBox()
        self.ip_address = swing.JTextArea('', 2, 100)
        self.ip_address.setLineWrap(True)
        self.ip_address.border = swing.BorderFactory.createTitledBorder("IP Address: ")
        box_horizontal.add(self.ip_address)
        box_vertical.add(box_horizontal)
        
        box_horizontal = swing.Box.createHorizontalBox()
        self.user_command = swing.JTextArea('', 2, 100)
        self.user_command.setLineWrap(True)
        self.user_command.border = swing.BorderFactory.createTitledBorder("Command: ")
        box_horizontal.add(self.user_command)
        box_vertical.add(box_horizontal)
        
        # Add buttons for functionality
        box_horizontal = swing.Box.createHorizontalBox()
        button_panel = swing.JPanel()
        
        self.connect_button = swing.JButton("Connect", actionPerformed=self.connect)
        self.send_button = swing.JButton("Send", actionPerformed=self.send)
        self.disconnect_button = swing.JButton("Disconnect", actionPerformed=self.disconnect)
        
        self.disconnect_button.enabled = False
        self.send_button.enabled = False
        
        button_panel.add(self.connect_button)
        button_panel.add(self.send_button)
        button_panel.add(self.disconnect_button)
        
        box_horizontal.add(button_panel)
        box_vertical.add(box_horizontal)        

        box_horizontal = swing.Box.createHorizontalBox()
        self.output = swing.JTextArea('', 25, 100)
        self.output.setLineWrap(True)
        self.output.setEditable(False)
        
        scroll = swing.JScrollPane(self.output)
        
        box_horizontal.add(scroll)
        box_vertical.add(box_horizontal)
        
        text_panel.add(box_vertical)
        
        self.tab.add(text_panel)
        
        callbacks.addSuiteTab(self)
        return

    def getTabCaption(self):
        return "Unencrypted Bind Shell"

    def getUiComponent(self):
        return self.tab

    def send(self, event):
        self.clicked = True
        time.sleep(1)
        self.output.text = self.response_data
        
    def send_data(self):
        while True:
            if self.kill_thread:
                sys.exit()
            
            if self.clicked:
                self.clicked = False
                self.s.send(self.user_command.text)
    
    def receive_data(self):
        while True:
            if self.kill_thread:
                sys.exit()
            
            data = self.s.recv(4096)
            
            if data:
                self.response_data = data
    
    def connect(self, event):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((self.ip_address.text, 1234))
            self.kill_thread = False
            
            threading.Thread(target=self.send_data).start()
            threading.Thread(target=self.receive_data).start()
            
            self.connect_button.enabled = False
            self.disconnect_button.enabled = True
            self.send_button.enabled = True
            
            self.output.text = "Connected to " + self.ip_address.text
        except Exception as e:
            self.output.text = "Failed to connect to " + self.ip_address.text
    
    def disconnect(self, event):
        self.s.send(b"exit\n")
        self.s.close()
        self.kill_thread = True
        
        self.connect_button.enabled = True
        self.disconnect_button.enabled = False
        self.send_button.enabled = False
        self.ip_address.enabled = True
        
        self.output.text = "Disconnected from " + self.ip_address.text

FixBurpExceptions()