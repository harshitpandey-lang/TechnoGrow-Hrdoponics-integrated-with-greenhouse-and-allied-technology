import serial
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime

# --- Connect to Arduino ---
ser = serial.Serial('COM5', 9600)  # ⚠️ Change COM5 if needed

# --- Initialize DataFrame ---
data = pd.DataFrame(columns=['Time', 'Temperature (°C)', 'Humidity (%)', 'MQ4 (%)'])

# --- Dashboard Style ---
plt.style.use('seaborn-v0_8-darkgrid')
fig, ax = plt.subplots(figsize=(11, 6))
fig.suptitle("🌡️ DHT11 + MQ4 Real-Time Dashboard", fontsize=20, fontweight='bold', color="#222831")
subtitle = fig.text(0.5, 0.93, "Monitoring Temperature, Humidity, and Gas Levels in Real Time",
                    ha='center', fontsize=11, color="#555555")

# --- Create text boxes for live readings (moved to bottom-left) ---
temp_text = ax.text(0.02, 0.12, '', transform=ax.transAxes, fontsize=12,
                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='gray'))
hum_text = ax.text(0.02, 0.07, '', transform=ax.transAxes, fontsize=12,
                   bbox=dict(facecolor='white', alpha=0.7, edgecolor='gray'))
gas_text = ax.text(0.02, 0.02, '', transform=ax.transAxes, fontsize=12,
                   bbox=dict(facecolor='white', alpha=0.7, edgecolor='gray'))
status_text = ax.text(0.70, 0.95, '', transform=ax.transAxes, fontsize=13, fontweight='bold',
                      bbox=dict(facecolor='white', alpha=0.8, edgecolor='black'))

# --- Animation Function ---
def animate(i):
    global data
    line = ser.readline().decode('utf-8').strip()

    if line.startswith("DATA"):
        try:
            _, t, h, mq4 = line.split(',')
            t, h, mq4 = float(t), float(h), float(mq4)
            time_now = datetime.now().strftime("%H:%M:%S")

            # Append data
            data.loc[len(data)] = [time_now, t, h, mq4]

            # Keep last 50 readings
            if len(data) > 50:
                data = data.iloc[-50:]

            # Smooth background color depending on gas level
            if mq4 > 80:
                bg_color = "#ffe6e6"  # light red
                status = "⚠️ High Gas Detected!"
                status_color = "red"
            elif mq4 > 50:
                bg_color = "#fff3cd"  # yellow
                status = "🟡 Moderate Gas Level"
                status_color = "#c58b00"
            else:
                bg_color = "#e6ffe6"  # light green
                status = "✅ Safe Environment"
                status_color = "green"

            ax.clear()
            ax.set_facecolor(bg_color)

            # --- Plot lines ---
            ax.plot(data['Time'], data['Temperature (°C)'], 'r-o', linewidth=2, markersize=6,
                    label='Temperature (°C)')
            ax.plot(data['Time'], data['Humidity (%)'], 'b-o', linewidth=2, markersize=6,
                    label='Humidity (%)')
            ax.plot(data['Time'], data['MQ4 (%)'], 'g-o', linewidth=2, markersize=6,
                    label='Gas Level (%)')

            # Beautify the plot
            ax.legend(loc='upper left', fontsize=10)
            ax.set_xlabel('⏱️ Time', fontsize=11, color="#222831")
            ax.set_ylabel('📏 Sensor Values', fontsize=11, color="#222831")
            plt.xticks(rotation=45, ha='right')
            ax.grid(True, alpha=0.4)
            plt.tight_layout(rect=[0, 0, 1, 0.94])

            # --- Update text boxes ---
            temp_text.set_text(f"🌡️ Temperature: {t:.1f} °C")
            hum_text.set_text(f"💧 Humidity: {h:.1f} %")
            gas_text.set_text(f"🧪 Gas Level: {mq4:.1f} %")
            status_text.set_text(status)
            status_text.set_color(status_color)

            # --- Re-attach text boxes ---
            ax.add_artist(temp_text)
            ax.add_artist(hum_text)
            ax.add_artist(gas_text)
            ax.add_artist(status_text)

        except Exception as e:
            print("Parsing error:", e, "Line:", line)


# --- Animate every 3 seconds ---
ani = animation.FuncAnimation(fig, animate, interval=3000)
plt.show()
