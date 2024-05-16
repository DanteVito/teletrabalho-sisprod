COUNTER_PERIODOS = 0
periodos = []

function adiciona_periodo() {
  // hidden_date()
  reorderItems()
  add_date()
}

function hidden_date() {
  Array.from(document.querySelectorAll("[id^='periodo-']"))
    .forEach((periodo, i) => {
      //console.log(periodo, i)
      periodo.style.display = "none"
    })
  reorderItems()
}

function add_date() {
  // adiciona o período na tela
  //var periodo = document.getElementById("periodo-" + COUNTER_PERIODOS)

  var ul = document.querySelector("[id=periodos-adicionados]")
  var li = document.createElement("li")
  li.setAttribute("id", "li-periodo-" + COUNTER_PERIODOS)

  try {
    data_inicio = document.querySelector("[id=id_data_inicio]")
    data_fim = document.querySelector("[id=id_data_fim]")
    var inputValue = data_inicio.value + ' a ' + data_fim.value
  }

  catch {
    data_inicio = document.querySelector("[id=id_render_periodoteletrabalho_plano_trabalho-" + COUNTER_PERIODOS + "-data_inicio]")
    data_fim = document.querySelector("[id=id_render_periodoteletrabalho_plano_trabalho-" + COUNTER_PERIODOS + "-data_fim]")
  }

  if (data_inicio.value === '') {
    alert("insira um valor para a data inicial!")
    hidden_date()
    return
  }

  if (data_fim.value === '') {
    alert("insira um valor para a data final!")
    hidden_date()
    return
  }

  var inputValue = data_inicio.value + ' a ' + data_fim.value
  var t = document.createTextNode(inputValue)
  var a = document.createElement("a")
  a.setAttribute('count-periodo', COUNTER_PERIODOS)
  a.innerText = '[X]'

  a.addEventListener('click', function (ev) {
    li.remove()
    count_periodo = a.getAttribute('count-periodo')
    var periodo = document.getElementById("periodo-" + count_periodo)
    periodo.remove()
    reorderItems()
  })

  li.appendChild(t)
  li.appendChild(a)
  ul.appendChild(li)

  // criar o elemento com o atributo da COUNTER_PERIODOS, para depois criar uma função que remove o período
  COUNTER_PERIODOS++
  reorderItems()
}

function reorderItems_periodos() {
  // periodo
  Array.from(document.querySelectorAll("[id^='periodo-']"))
    .forEach((periodo, i) => {
      periodo.setAttribute('id', 'periodo-' + i)
      if (i >= 0) {
        console.log(i)
        console.log(periodo.querySelector('[type="hidden"]'))
        console.log(periodo.querySelector('[data-field="data_inicio"]'))
        console.log(periodo.querySelector('[data-field="data_fim"]'))

        periodo.querySelector('[type="hidden"]').setAttribute('name', 'render_periodoteletrabalho_plano_trabalho-' + i + '-' + 'plano_trabalho')
        periodo.querySelector('[data-field="data_inicio"]').setAttribute('name', 'render_periodoteletrabalho_plano_trabalho-' + i + '-' + 'data_inicio')
        periodo.querySelector('[data-field="data_fim"]').setAttribute('name', 'render_periodoteletrabalho_plano_trabalho-' + i + '-' + 'data_fim')

        periodo.querySelector('[type="hidden"]').setAttribute('id', 'id_render_periodoteletrabalho_plano_trabalho-' + i + '-' + 'plano_trabalho')
        periodo.querySelector('[data-field="data_inicio"]').setAttribute('id', 'id_render_periodoteletrabalho_plano_trabalho-' + i + '-' + 'data_inicio')
        periodo.querySelector('[data-field="data_fim"]').setAttribute('id', 'id_render_periodoteletrabalho_plano_trabalho-' + i + '-' + 'data_fim')
      }

      plano_trabalho = document.querySelector("[id=id_render_periodoteletrabalho_plano_trabalho-" + COUNTER_PERIODOS + "-plano_trabalho]")
      data_inicio = document.querySelector("[id=id_render_periodoteletrabalho_plano_trabalho-" + COUNTER_PERIODOS + "-data_inicio]")
      data_fim = document.querySelector("[id=id_render_periodoteletrabalho_plano_trabalho-" + COUNTER_PERIODOS + "-data_fim]")
    }
    );

  let totalPeriodos = document.querySelectorAll("[id^='periodo-']").length;
  document.querySelector('#id_render_periodoteletrabalho_plano_trabalho-TOTAL_FORMS').value = totalPeriodos;
}

function reorderItems_atividades() {
  // atividade
  Array.from(document.querySelectorAll("[id^='atividade-']"))
    .forEach((periodo, i) => {
      periodo.setAttribute('id', 'atividade-' + i)
      if (i > 0) {
        console.log(periodo.querySelector('[data-field="periodo"]'))
        console.log(periodo.querySelector('[data-field="atividade"]'))
        console.log(periodo.querySelector('[data-field="meta_qualitativa"]'))
        console.log(periodo.querySelector('[data-field="tipo_meta_quantitativa"]'))
        console.log(periodo.querySelector('[data-field="meta_quantitativa"]'))

        periodo.querySelector('[data-field="periodo"]').setAttribute('name', 'render_atividadesteletrabalho_periodo-' + i + '-' + 'periodo')
        periodo.querySelector('[data-field="atividade"]').setAttribute('name', 'render_atividadesteletrabalho_periodo-' + i + '-' + 'atividade')
        periodo.querySelector('[data-field="meta_qualitativa"]').setAttribute('name', 'render_atividadesteletrabalho_periodo-' + i + '-' + 'meta_qualitativa')
        periodo.querySelector('[data-field="tipo_meta_quantitativa"]').setAttribute('name', 'render_atividadesteletrabalho_periodo-' + i + '-' + 'tipo_meta_quantitativa')
        periodo.querySelector('[data-field="meta_quantitativa"]').setAttribute('name', 'render_atividadesteletrabalho_periodo-' + i + '-' + 'meta_quantitativa')

        periodo.querySelector('[data-field="periodo"]').setAttribute('id', 'id_render_atividadesteletrabalho_periodo-' + i + '-' + 'periodo')
        periodo.querySelector('[data-field="atividade"]').setAttribute('id', 'id_render_atividadesteletrabalho_periodo-' + i + '-' + 'atividade')
        periodo.querySelector('[data-field="meta_qualitativa"]').setAttribute('id', 'id_render_atividadesteletrabalho_periodo-' + i + '-' + 'meta_qualitativa')
        periodo.querySelector('[data-field="tipo_meta_quantitativa"]').setAttribute('id', 'id_render_atividadesteletrabalho_periodo-' + i + '-' + 'tipo_meta_quantitativa')
        periodo.querySelector('[data-field="meta_quantitativa"]').setAttribute('id', 'id_render_atividadesteletrabalho_periodo-' + i + '-' + 'meta_quantitativa')
      }
    }
    );

  let totalAtividades = document.querySelectorAll("[id^='atividade-']").length;
  document.querySelector('#id_render_atividadesteletrabalho_periodo-TOTAL_FORMS').value = totalAtividades;
}

function reorderItems() {
  reorderItems_periodos()
  reorderItems_atividades()
}