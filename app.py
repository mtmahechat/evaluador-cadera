from datetime import date, datetime
import math
import streamlit as st

# Configuración de la página móvil
st.set_page_config(
    page_title="Evaluador Acetabular", page_icon="🦴", layout="centered"
)


def norm_cdf(z):
  return 0.5 * math.erfc(-z / math.sqrt(2))


def obtener_lms(sexo: str, edad_anios: float):
  t = edad_anios
  if sexo == "Masculino":
    l = 0.834 - 0.028 * t
    m = 25.297 - 2.721 * t + 0.201 * (t**2) - 0.006 * (t**3)
    s = 0.128 + 0.030 * t - 0.001 * (t**2)
  else:  # Femenino
    l = 0.279 - 0.029 * t
    m = 26.289 - 2.415 * t + 0.188 * (t**2) - 0.008 * (t**3)
    s = 0.150 + 0.011 * t - 0.0006 * (t**2)
  return l, m, s


def evaluar_cadera(ia_medido: float, l: float, m: float, s: float):
  z_score = (((ia_medido / m) ** l) - 1) / (l * s)
  percentil = norm_cdf(z_score) * 100.0

  if percentil < 50.0:
    diag = "NORMAL"
    color = "green"
    rec = "Desarrollo acetabular adecuado para la edad."
  elif 50.0 <= percentil <= 90.0:
    diag = "EN RIESGO / LÍMITE"
    color = "orange"
    rec = "Zona de monitoreo: dar seguimiento a la evolución de la remodelación."
  else:
    diag = "DISPLASIA ACETABULAR"
    color = "red"
    rec = "Zona crítica (> P90): requiere evaluación u orientación terapéutica."

  return z_score, percentil, diag, color, rec


# --- INTERFAZ GRÁFICA (UI) ---
st.title("🦴 Evaluador Acetabular (AA)")
st.caption("Basado en curvas de percentiles de Novais et al. (2018)")
st.caption("Normal Percentile Reference Curves and Correlation of Acetabular Index and Acetabular Depth Ratio in Children. J Pediatr Orthop. 2018 Mar;38(3):163-169.")
st.subheader("Datos del Paciente")
col1, col2 = st.columns(2)

with col1:
  fn = st.date_input(
      "Fecha de Nacimiento",
      value=date(2023, 1, 1),
      min_value=date(2008, 1, 1),
      max_value=date.today(),
  )
  sexo = st.radio("Sexo", ["Femenino", "Masculino"])

with col2:
  frx = st.date_input(
      "Fecha de Radiografía", value=date.today(), max_value=date.today()
  )

st.subheader("Mediciones Radiológicas (a la ceja o sourcil)")
col_der, col_izq = st.columns(2)

with col_der:
  ia_der = st.number_input(
      "Ángulo Derecho (°)", min_value=0.0, max_value=50.0, value=22.0, step=0.5
  )

with col_izq:
  ia_izq = st.number_input(
      "Ángulo Izquierdo (°)",
      min_value=0.0,
      max_value=50.0,
      value=27.0,
      step=0.5,
  )

# --- BOTÓN Y CÁLCULOS ---
if st.button("Evaluar Caderas", type="primary", use_container_width=True):
  dias = (frx - fn).days
  edad_anios = dias / 365.25

  if dias < 0:
    st.error("Error: La fecha de la radiografía no puede ser previa al nacimiento.")
  elif edad_anios > 14.0:
    st.warning(
        f"El paciente tiene {edad_anios:.2f} años. El estudio de Novais et al."
        " está validado hasta los 14 años."
    )
  else:
    l, m, s = obtener_lms(sexo, edad_anios)

    z_der, p_der, diag_der, color_der, rec_der = evaluar_cadera(ia_der, l, m, s)
    z_izq, p_izq, diag_izq, color_izq, rec_izq = evaluar_cadera(ia_izq, l, m, s)

    st.markdown("---")
    st.info(
        f"**Edad al examen:** {edad_anios:.2f} años ({dias} días) | **Media"
        f" esperada (P50):** {m:.1f}°"
    )

    # Resultados Cadera Derecha
    st.markdown("### Cadera Derecha")
    st.markdown(f":{color_der}[**Clasificación: {diag_der}**]")
    st.write(f"- **Percentil:** P{p_der:.1f} (Z-score: {z_der:+.2f})")
    st.write(f"- **Conducta:** {rec_der}")

    # Resultados Cadera Izquierda
    st.markdown("### Cadera Izquierda")
    st.markdown(f":{color_izq}[**Clasificación: {diag_izq}**]")
    st.write(f"- **Percentil:** P{p_izq:.1f} (Z-score: {z_izq:+.2f})")
    st.write(f"- **Conducta:** {rec_izq}")
