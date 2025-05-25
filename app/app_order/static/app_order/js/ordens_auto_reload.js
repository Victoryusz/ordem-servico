// Atualiza a tabela de ordens automaticamente a cada 10s
async function atualizarTabelaOS() {
    try {
      const response = await fetch("/api/os-funcionario/");
      const ordens = await response.json();
      const tbody = document.querySelector("#tabela-os tbody");
      if (!tbody) return;
  
      tbody.innerHTML = "";
  
      ordens.forEach(os => {
        let badge = "";
        if (os.status === "concluida") {
          badge = `<span class="badge bg-success"><i class="bi bi-check-circle-fill me-1"></i>Concluído</span>`;
        } else if (os.status === "em_andamento") {
          badge = `<span class="badge bg-info"><i class="bi bi-hourglass-split me-1"></i>Em andamento</span>`;
        } else {
          badge = `<span class="badge bg-warning text-dark"><i class="bi bi-clock-fill me-1"></i>Aguardando</span>`;
        }
  
        let acoes = "";
        if (os.status !== "concluida" && os.numero_os) {
          acoes = `
            <a href="/painel-funcionario/concluir-os/${os.numero_os}/" class="btn btn-success btn-sm">
              <i class="bi bi-check2-square"></i> Concluir
            </a>
          `;
        } else {
          acoes = `<span class="text-muted">—</span>`;
        }
  
        tbody.innerHTML += `
          <tr>
            <td>${os.numero_os || "—"}</td>
            <td>${os.nome_cliente}</td>
            <td>${os.descricao}</td>
            <td>${badge}</td>
            <td>${acoes}</td>
          </tr>`;
      });
    } catch (error) {
      console.error("Erro ao atualizar tabela:", error);
    }
  }
  
  setInterval(atualizarTabelaOS, 10000);
  