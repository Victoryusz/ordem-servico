document.addEventListener("DOMContentLoaded", () => {
  const numeroEl = document.getElementById("numero-os");
  if (!numeroEl) return;

  const statusEl = document.getElementById("status-os");
  const pk       = numeroEl.dataset.pk;
  const url      = `/api/verificar-numero-os/${pk}/`;

  async function verificarOS() {
    try {
      const res  = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      // Atualiza número (apenas se ainda estiver mostrando "Aguardando")
      if (data.numero_os && statusEl.textContent.includes("Aguardando")) {
        numeroEl.textContent = data.numero_os;
      }

      // Atualiza badge de status
      if (data.status) {
        let html, cls;

        switch (data.status) {
          case "aguardando":
            html = `
              Aguardando…
              <span class="spinner-border spinner-border-sm text-dark ms-2" role="status">
                <span class="visually-hidden">Carregando…</span>
              </span>`;
            cls = "badge bg-warning text-dark d-inline-flex align-items-center";
            break;

          case "em_andamento":
            html = 'Confirmado <i class="bi bi-check-circle-fill ms-1"></i>';
            cls  = "badge bg-success text-white";
            break;

          case "concluida":
            html = 'Concluída <i class="bi bi-check-circle-fill ms-1"></i>';
            cls  = "badge bg-success text-white";
            break;

          default:
            html = data.status;
            cls  = "badge bg-secondary text-white";
        }

        statusEl.className = cls;
        statusEl.innerHTML = html;
      }
    } catch (err) {
      console.error("Erro ao verificar OS:", err);
    }
  }

  // primeira chamada + polling a cada 5s
  verificarOS();
  setInterval(verificarOS, 5000);
});
