import pandas as pd
import numpy as np
import streamlit as st

st.title("Mini Gage R&R App")
st.subheader("(2 Prüfer, 3 Teile, 2 Messungen)")

st.subheader("Messungen")

# Neue strukturierte Tabelle
default_data = {
    "Teil": ["1", "2", "3"] * 2,
    "Prüfer": ["A"] * 3 + ["B"] * 3,
    "Messung 1": [30.0, 30.0, 30.0, 30.0, 30.0, 30.0],
    "Messung 2": [30.0, 30.0, 30.0, 30.0, 30.0, 30.0]
}

df = st.data_editor(pd.DataFrame(default_data), num_rows="dynamic")

# Mittelwert und Wiederholbarkeit je Zeile
df["Mittelwert"] = df[["Messung 1", "Messung 2"]].mean(axis=1)
df["Std"] = df[["Messung 1", "Messung 2"]].std(axis=1, ddof=1)

# EV: mittlere Wiederholabweichung
EV = df["Std"].mean()

# AV: Standardabweichung der Mittelwerte zwischen Prüfern je Teil
mittel_df = df.pivot(index="Teil", columns="Prüfer", values="Mittelwert")
diffs = mittel_df["A"] - mittel_df["B"]
AV_var = np.mean(diffs ** 2)

# Korrektur der AV um EV² / n
AV_corrected = AV_var - (EV**2 / 2)
AV = np.sqrt(AV_corrected) if AV_corrected > 0 else 0

# R&R
RR = np.sqrt(EV**2 + AV**2)

# Gesamtstreuung (über alle Einzelmessungen)
all_measurements = df[["Messung 1", "Messung 2"]].values.flatten()
total_std = np.std(all_measurements, ddof=1)

# R&R-Anteil
rr_percent = (RR / total_std) * 100 if total_std > 0 else np.nan

st.subheader("Zwischenrechnungen & Formeln")

st.markdown("#### 1. Mittelwerte und Wiederholbarkeit (EV)")

st.latex(r"""
\text{Mittelwert}_{ij} = \frac{x_{ij1} + x_{ij2}}{2}
""")
st.latex(r"""
\text{EV}_{ij} = \sqrt{\frac{(x_{ij1} - \bar{x}_{ij})^2 + (x_{ij2} - \bar{x}_{ij})^2}{1}}
""")

for i, row in df.iterrows():
    st.markdown(f"- Teil {row['Teil']}, Prüfer {row['Prüfer']}: Mittelwert = {row['Mittelwert']:.2f}, Std = {row['Std']:.4f}")

st.markdown(f"→ **EV (Mittel der Wiederholstandardabweichungen):** {EV:.4f}")

st.markdown("#### 2. Reproduzierbarkeit (AV)")

st.latex(r"""
\text{Differenz}_i = \bar{x}_{iA} - \bar{x}_{iB}
""")
st.latex(r"""
\text{AV-Varianz} = \frac{1}{n} \sum_{i=1}^n (\text{Differenz}_i)^2
""")
st.latex(r"""
\text{Korrektur} = \frac{EV^2}{2}
""")
st.latex(r"""
\text{AV} = \sqrt{\text{AV-Varianz} - \text{Korrektur}}
""")

for teil in mittel_df.index:
    a = mittel_df.loc[teil, "A"]
    b = mittel_df.loc[teil, "B"]
    diff = a - b
    st.markdown(f"- Teil {teil}: {a:.2f} − {b:.2f} = {diff:.4f} → Quadrat = {diff**2:.6f}")

st.markdown(f"→ **AV-Varianz:** {AV_var:.6f}  \n→ Korrekturterm (EV²/2): {EV**2/2:.6f}  \n→ **AV:** {AV:.4f}")

st.markdown("#### 3. Gesamtstreuung und R&R-Anteil")

st.latex(r"""
\text{R\&R} = \sqrt{EV^2 + AV^2}
""")
st.latex(r"""
\text{R\&R-Anteil} = \frac{\text{R\&R}}{\text{Gesamtstreuung}} \times 100
""")

# Ausgabe
st.subheader("Gage R&R Auswertung")

st.markdown(f"""
- **EV (Wiederholbarkeit):** {EV:.3f}  
- **AV (Reproduzierbarkeit):** {AV:.3f}  
- **Gesamte Messsystemstreuung (R&R):** {RR:.3f}  
- **Gesamtstreuung:** {total_std:.3f}  
- **R&R-Anteil an Gesamtstreuung:** {rr_percent:.1f}%
""")
