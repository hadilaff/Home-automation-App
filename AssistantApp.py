
import tkinter as tk
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
from PIL import Image, ImageTk

# time for the “Motion Detected” message to disappear in milliseconds
MOTION_MESSAGE_DELAY = 5000  # 5000 ms = 5 secondes


def display_image():
    # addimage
    img = Image.open("icon2.jpg")  
    img = img.resize((100, 100), Image.LANCZOS)  

    # Convert the image to a format compatible with Tkinter
    img_tk = ImageTk.PhotoImage(img)

    # create  etiquette for displaying the image
    image_label = tk.Label(window, image=img_tk)
    image_label.image = img_tk  # make a reference for the image 
    #image_label.grid(row=2, column=1, columnspan=2, padx=10, pady=10)
    image_label.grid(row=1, column=1, columnspan=2, padx=10, pady=10)

def publish_led_off():
    # Publish the message "led_off" to the "control" topic
    publish.single("control", "led_off", hostname="broker.hivemq.com")

def publish_led_on():
    # Publish the message "led_on" to the "control" topic
    publish.single("control", "led_on", hostname="broker.hivemq.com")


#update LDR, Humidity, Temperature values
def on_message_ldr(client, userdata, msg):
    ldr_value.set("LDR: " + msg.payload.decode("utf-8"))

def on_message_humidity(client, userdata, msg):
    humidity_value.set("Humidity: " + msg.payload.decode("utf-8"))

def on_message_temperature(client, userdata, msg):
    temperature_value.set("Temperature: " + msg.payload.decode("utf-8"))

def on_message_motion(client, userdata, msg):
    motion_detected.set(True)
    motion_label.config(text="Motion Detected !!", fg="red")
    #  Start a countdown to reset the message after a certain time
    window.after(MOTION_MESSAGE_DELAY, reset_motion_message)

def reset_motion_message():
    motion_detected.set(False)
    motion_label.config(text="")

def subscribe_ldr():
    # Subscribe to LDR topic
    client.subscribe("LDR")
    client.message_callback_add("LDR", on_message_ldr)

def subscribe_humidity():
    # Subscribe to humidity topic
    client.subscribe("humidity")
    client.message_callback_add("humidity", on_message_humidity)

def subscribe_temperature():
    # Subscribe to temperature topic
    client.subscribe("temp")
    client.message_callback_add("temp", on_message_temperature)

def subscribe_motion():
    # Subscribe to motion topic
    client.subscribe("motion")
    client.message_callback_add("motion", on_message_motion)

# Create main window, the front of the app
window = tk.Tk()
window.title("My Home Security")
window.configure(bg="#9cdfe1")


title_label = tk.Label(window, text="Light Control", font=("Helvetica", 16, "bold"), bg="#9cdfe1")
title_label.grid(row=0, column=1, columnspan=2, padx=10, pady=10)

display_image()
publish_button = tk.Button(window, text="Publish On", command=publish_led_on, bg="green", fg="white", activebackground="darkgreen", activeforeground="white", font=("Helvetica", 12))
#publish_button = tk.Button(window, text="Publish On", command=publish_led_on)
publish_button.grid(row=1, column=0, columnspan=2, pady=10)

publish_off_button = tk.Button(window, text="Publish Off", command=publish_led_off, bg="red", fg="white", activebackground="darkred", activeforeground="white", font=("Helvetica", 12))
#publish_off_button = tk.Button(window, text="Publish Off", command=publish_led_off)
publish_off_button.grid(row=1, column=3, columnspan=3, pady=10)

# Create widgets for subscribing
subscribe_ldr_button = tk.Button(window, text="Subscribe LDR", command=subscribe_ldr, bg="#EDA390", fg="white", activebackground="darkblue", activeforeground="white", font=("Helvetica", 12))
#subscribe_ldr_button = tk.Button(window, text="Subscribe LDR", command=subscribe_ldr)
subscribe_humidity_button = tk.Button(window, text="Subscribe Humidity", command=subscribe_humidity, bg="#F7B586", fg="white", activebackground="darkblue", activeforeground="white", font=("Helvetica", 12))
#subscribe_humidity_button = tk.Button(window, text="Subscribe Humidity", command=subscribe_humidity)

subscribe_temperature_button = tk.Button(window, text="Subscribe Temperature", command=subscribe_temperature, bg="#EBAB92", fg="white", activebackground="darkblue", activeforeground="white", font=("Helvetica", 12))
#subscribe_temperature_button = tk.Button(window, text="Subscribe Temperature", command=subscribe_temperature)
subscribe_motion_button = tk.Button(window, text="Subscribe Motion", command=subscribe_motion, bg="#F08D9C", fg="white", activebackground="darkblue", activeforeground="white", font=("Helvetica", 12))

#subscribe_motion_button = tk.Button(window, text="Subscribe Motion", command=subscribe_motion)

# Create variables to store sensor values
ldr_value = tk.StringVar()
humidity_value = tk.StringVar()
temperature_value = tk.StringVar()
motion_detected = tk.BooleanVar()

# Create labels to display sensor values
ldr_label = tk.Label(window, textvariable=ldr_value)
humidity_label = tk.Label(window, textvariable=humidity_value)
temperature_label = tk.Label(window, textvariable=temperature_value)

# Create a label for motion detection
motion_label = tk.Label(window, text="", fg="red")

# Arrange widgets using grid
subscribe_ldr_button.grid(row=2, column=0, pady=10)
subscribe_humidity_button.grid(row=2, column=1, pady=10)
subscribe_temperature_button.grid(row=2, column=2, pady=10)
subscribe_motion_button.grid(row=4, column=1, pady=10)

ldr_label.grid(row=3, column=0, padx=10, pady=10)
humidity_label.grid(row=3, column=1, padx=10, pady=10)
temperature_label.grid(row=3, column=2, padx=10, pady=10)
motion_label.grid(row=6, column=1, padx=10, pady=10)


##ADD A HOME IMAGE
img_motion = Image.open("home.png")  # path of the image
img_motion = img_motion.resize((150, 150), Image.LANCZOS)  # Resize the image
img_motion_tk = ImageTk.PhotoImage(img_motion)
motion_image_label = tk.Label(window, image=img_motion_tk)
motion_image_label.image = img_motion_tk  

#the position of the image
motion_image_label.grid(row=7, column=1, padx=10, pady=10)



# Connect to broker
client = mqtt.Client()
client.connect("broker.hivemq.com")  # Connect to a broker

# Start the loop to process incoming messages
client.loop_start()
window.geometry("600x500")

# Start the GUI event loop
window.mainloop()
