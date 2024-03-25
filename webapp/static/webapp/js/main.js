function reorderItems() {
    // periodo
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

    // atividade
    Array.from(document.querySelectorAll("[id^='atividade-']"))
      .forEach((periodo, i) => {
        periodo.setAttribute('id', 'atividade-' + i)
        if (i > 0) {
            console.log(periodo.querySelector('[data-field="periodo"'))
            console.log(periodo.querySelector('[data-field="atividade"'))
            console.log(periodo.querySelector('[data-field="meta_qualitativa"'))
            console.log(periodo.querySelector('[data-field="tipo_meta_quantitativa"'))
            console.log(periodo.querySelector('[data-field="meta_quantitativa"'))

            periodo.querySelector('[data-field="periodo"').setAttribute('name', 'render_atividadesteletrabalho_periodo-' + i + '-' + 'periodo')
            periodo.querySelector('[data-field="atividade"').setAttribute('name', 'render_atividadesteletrabalho_periodo-' + i + '-' + 'atividade')
            periodo.querySelector('[data-field="meta_qualitativa"').setAttribute('name', 'render_atividadesteletrabalho_periodo-' + i + '-' + 'meta_qualitativa')
            periodo.querySelector('[data-field="tipo_meta_quantitativa"').setAttribute('name', 'render_atividadesteletrabalho_periodo-' + i + '-' + 'tipo_meta_quantitativa')
            periodo.querySelector('[data-field="meta_quantitativa"').setAttribute('name', 'render_atividadesteletrabalho_periodo-' + i + '-' + 'meta_quantitativa')

            periodo.querySelector('[data-field="periodo"').setAttribute('id', 'id_render_atividadesteletrabalho_periodo-' + i + '-' + 'periodo')
            periodo.querySelector('[data-field="atividade"').setAttribute('id', 'id_render_atividadesteletrabalho_periodo-' + i + '-' + 'atividade')
            periodo.querySelector('[data-field="meta_qualitativa"').setAttribute('id', 'id_render_atividadesteletrabalho_periodo-' + i + '-' + 'meta_qualitativa')
            periodo.querySelector('[data-field="tipo_meta_quantitativa"').setAttribute('id', 'id_render_atividadesteletrabalho_periodo-' + i + '-' + 'tipo_meta_quantitativa')
            periodo.querySelector('[data-field="meta_quantitativa"').setAttribute('id', 'id_render_atividadesteletrabalho_periodo-' + i + '-' + 'meta_quantitativa')
        }
        }
      );

      let totalAtividades = document.querySelectorAll("[id^='atividade-']").length;
      document.querySelector('#id_render_atividadesteletrabalho_periodo-TOTAL_FORMS').value = totalAtividades;
    }