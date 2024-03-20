function reorderItems() {
    Array.from(document.querySelectorAll("[id^='periodo-']"))
      .forEach((periodo, i) => {
        periodo.setAttribute('id', 'periodo-' + i)
        if (i > 0) {
            console.log(periodo.querySelector('[data-field="plano_trabalho"'))
            console.log(periodo.querySelector('[data-field="data_inicio"'))
            console.log(periodo.querySelector('[data-field="data_fim"'))
    
            periodo.querySelector('[data-field="plano_trabalho"').setAttribute('name', 'render_periodoteletrabalho_plano_trabalho-' + i + '-' + 'plano_trabalho')
            periodo.querySelector('[data-field="data_inicio"').setAttribute('name', 'render_periodoteletrabalho_plano_trabalho-' + i + '-' + 'data_inicio')
            periodo.querySelector('[data-field="data_fim"').setAttribute('name', 'render_periodoteletrabalho_plano_trabalho-' + i + '-' + 'data_fim')
    
            periodo.querySelector('[data-field="plano_trabalho"').setAttribute('id', 'id_render_periodoteletrabalho_plano_trabalho-' + i + '-' + 'plano_trabalho')
            periodo.querySelector('[data-field="data_inicio"').setAttribute('id', 'id_render_periodoteletrabalho_plano_trabalho-' + i + '-' + 'data_inicio')
            periodo.querySelector('[data-field="data_fim"').setAttribute('id', 'id_render_periodoteletrabalho_plano_trabalho-' + i + '-' + 'data_fim')
        }
        }
      );
      let totalPeriodos = document.querySelectorAll("[id^='periodo-']").length;
      document.querySelector('#id_render_periodoteletrabalho_plano_trabalho-TOTAL_FORMS').value = totalPeriodos;
    }