# import matplotlib.pyplot as plt
# import numpy as np

# # Define data
# labels = ["G-API", "Proposed-1", "VOSK",  "Proposed-2", "Whisper", "Proposed -3"]
# values = [
#     [0.38,0.37,0.21,0.24,0.25,0.4,0.39,0.24,0.53,0.22],
#     [0.08,0.34,0.21,0.17,0.22,0.07,0.1,0.17,0.28,0.12],
#     [0.54,0.44,0.28,0.49,0.36,0.42,0.87,0.63,0.84,0.29],
#     [0.37,0.25,0.21,0.36,0.36,0.42,0.64,0.42,0.63,0.29],
#     [0.29,0.2,0.2,0.34,0.26,0.3,0.42,0.32,0.12,0.18],
#     [0.03,0.2,0.1,0.28,0.17,0.1,0.28,0.32,0.04,0.08]



# ]
# means = [np.mean(v) for v in values]
# stds = [np.std(v) for v in values]

# plt.figure(figsize=(8, 5))
# plt.bar(labels, means, yerr=stds, capsize=10, color='lightgreen', edgecolor='black')
# plt.ylabel("Mean Value")
# plt.title("Bar Plot with Mean ± SD")
# plt.tight_layout()
# plt.show()


import matplotlib.pyplot as plt
import numpy as np

# WER
wer_mean = [0.41, 0.19, 0.73, 0.47, 0.45, 0.33]
wer_sd = [0.15, 0.11, 0.26, 0.16, 0.24, 0.22]

# WPS
wps_mean = [1.53, 1.53, 1.81, 1.81, 1.34, 1.34]
wps_sd = [0.19, 0.19, 0.23, 0.23, 0.21, 0.21]

# CER
cer_mean = [0.32, 0.18, 0.52, 0.40, 0.26, 0.16]
cer_sd = [0.10, 0.08, 0.20, 0.14, 0.08, 0.10]

labels = ['G-API', 'Proposed_G-API', 'Vosk', 'Proposed_Vosk', 'Whisper', 'Proposed_Whisper']
x = np.arange(len(labels))
colors = ['#1f77b4', '#ff7f0e', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']

fig, axs = plt.subplots(1, 3, figsize=(16, 5), constrained_layout=True)

# WER plot
axs[0].bar(x, wer_mean, yerr=wer_sd, capsize=5, color=colors, width=0.6)
axs[0].set_title('Word Error Rate (WER)', fontsize=13)
axs[0].set_ylabel('WER')
axs[0].set_xticks(x)
axs[0].set_xticklabels(labels, rotation=45)
axs[0].grid(True, axis='y', linestyle='--', alpha=0.6)

# WPS plot
axs[1].bar(x, wps_mean, yerr=wps_sd, capsize=5, color=colors, width=0.6)
axs[1].axhline(y=1.33, color='black', linestyle='--', linewidth=1)
axs[1].axhline(y=2.25, color='black', linestyle='--', linewidth=1)
axs[1].set_title('Words Per Second (WPS)', fontsize=13)
axs[1].set_ylabel('WPS')
axs[1].set_xticks(x)
axs[1].set_xticklabels(labels, rotation=45)
axs[1].grid(True, axis='y', linestyle='--', alpha=0.6)

# CER plot
axs[2].bar(x, cer_mean, yerr=cer_sd, capsize=5, color=colors, width=0.6)
axs[2].set_title('Character Error Rate (CER)', fontsize=13)
axs[2].set_ylabel('CER')
axs[2].set_xticks(x)
axs[2].set_xticklabels(labels, rotation=45)
axs[2].grid(True, axis='y', linestyle='--', alpha=0.6)

fig.suptitle('Performance Comparison of Speech Models', fontsize=15, fontweight='bold')
plt.show()
