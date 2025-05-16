import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, ArrowStyle

# Set up the figure
fig, ax = plt.subplots(figsize=(12, 3))
ax.set_xlim(0, 16)
ax.set_ylim(0, 2)
ax.axis('off')

# Define nodes and positions
nodes = [
    "Audio Input",
    "STT (Google, Vosk, Whisper)",
    "Text Validation",
    "Grammar Checking (LanguageTool)",
    "Error Correction (LanguageTool, TextBlob)",
    "Result Compilation",
    "Storage (SQLite)",
    "User Feedback"
]
x_positions = [1, 3, 5, 7, 9, 11, 13, 15]

# Draw nodes
for x, label in zip(x_positions, nodes):
    box = FancyBboxPatch((x-0.8, 0.5), 1.6, 0.8, boxstyle="round,pad=0.3",
                         facecolor="#ADD8E6", edgecolor="black")
    ax.add_patch(box)
    ax.text(x, 0.9, label, ha="center", va="center", fontsize=8, color="white",
            wrap=True, bbox=dict(facecolor='none', edgecolor='none'))

# Draw arrows
for i in range(len(x_positions)-1):
    ax.annotate("", xy=(x_positions[i+1]-1, 0.9), xytext=(x_positions[i]+0.8, 0.9),
                arrowprops=dict(arrowstyle="->", color="#228B22", lw=2))

# Save the image
plt.savefig("grammar_architecture.png", bbox_inches="tight", transparent=True)
plt.close()