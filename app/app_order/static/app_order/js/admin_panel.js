// Mostrar detalhes da OS num modal Bootstrap
document.querySelectorAll('.btn-detalhes-os').forEach(btn => {
    btn.addEventListener('click', () => {
      const osId = btn.dataset.osId;
      const modalEl = document.getElementById('modalDetalhes');
      const body = document.getElementById('modalDetalhesBody');
  
      // mostra spinner antes de carregar
      body.innerHTML = `
        <div class="text-center py-5">
          <div class="spinner-border" role="status"><span class="visually-hidden">Carregando...</span></div>
        </div>
      `;
      const modal = new bootstrap.Modal(modalEl);
      modal.show();
  
      fetch(`/detalhes-os/${osId}/`)
        .then(r => r.text())
        .then(html => {
          body.innerHTML = html;
        })
        .catch(() => {
          body.innerHTML = '<div class="alert alert-danger">Erro ao carregar detalhes.</div>';
        });
    });
  });
  