COUNTER_PERIODOS = 0
COUNTER_ATIVIDADES = 0
periodos = []

function adiciona_periodo() {
  hidden_date()
  add_date()
}

function adiciona_atividade() {
  hidden_atividade()
  add_atividade()
}

function hidden_date() {
  Array.from(document.querySelectorAll("[id^='periodo-']"))
    .forEach((periodo, i) => {
      //console.log(periodo, i)
      periodo.style.display = "none"
    })
  last_periodo = document.querySelectorAll("[id^='periodo-']")[document.querySelectorAll("[id^='periodo-']").length - 1]
  last_periodo.setAttribute('count-periodo', COUNTER_PERIODOS)
}

function hidden_atividade() {
  Array.from(document.querySelectorAll("[id^='atividade-']"))
    .forEach((atividade, i) => {
      //console.log(atividade, i)
      atividade.style.display = "none"
    })
  last_atividade = document.querySelectorAll("[id^='atividade-']")[document.querySelectorAll("[id^='atividade-']").length - 1]
  last_atividade.setAttribute('count-atividade', COUNTER_PERIODOS)
}

function add_date() {
  // adiciona o período na tela

  var ul = document.querySelector("[id=periodos-adicionados]")
  var li = document.createElement("li")
  li.setAttribute("id", "li-periodo-" + COUNTER_PERIODOS)

  if (data_inicio = document.querySelector("[id=id_data_inicio]") == null) {
    data_inicio = document.querySelector("[id=id_render_periodoteletrabalho_plano_trabalho-" + COUNTER_PERIODOS + "-data_inicio]")
  } else {
    data_inicio = document.querySelector("[id=id_data_inicio]")
  }

  if (data_fim = document.querySelector("[id=id_data_fim]") == null) {
    data_fim = document.querySelector("[id=id_render_periodoteletrabalho_plano_trabalho-" + COUNTER_PERIODOS + "-data_fim]")
  } else {
    data_fim = document.querySelector("[id=id_data_fim]")
  }

  if (data_inicio.value === '') {
    alert("insira um valor para a data inicial!")
    periodos = document.querySelectorAll("[id^='periodo-']")
    ultimo = periodos[periodos.length - 1].remove()
    return
  }

  if (data_fim.value === '') {
    alert("insira um valor para a data final!")
    periodos = document.querySelectorAll("[id^='periodo-']")
    ultimo = periodos[periodos.length - 1].remove()
    return
  }

  var inputValue = data_inicio.value + ' a ' + data_fim.value
  var t = document.createTextNode(inputValue)
  var a = document.createElement("a")
  a.setAttribute('count-periodo', COUNTER_PERIODOS)
  a.innerText = ' - [X]'

  a.addEventListener('click', function (ev) {
    // depois de removermos os elementos não conseguimos mais adicionar porque 
    // ele não acha pelo count-periodo, tentar usar um try except aqui
    count_periodo = a.getAttribute('count-periodo')
    var periodo = document.querySelector('[count-periodo="' + count_periodo.toString() + '"]')
    periodo.remove()
    li.remove()
  })

  li.appendChild(t)
  li.appendChild(a)
  ul.appendChild(li)

  // criar o elemento com o atributo da COUNTER_PERIODOS, para depois criar uma função que remove o período
  COUNTER_PERIODOS++

  // reordena os itens
  reorderItems_periodos()
}

function add_atividade() {
  // adiciona a atividade na tela

  var ul = document.querySelector("[id=atividades-adicionadas]")
  var li = document.createElement("li")
  li.setAttribute("id", "li-atividade-" + COUNTER_ATIVIDADES)

  if (document.querySelector("[id=id_atividade]") === null) {
    atividade = document.querySelector("[id=id_render_atividadesteletrabalho_periodo-" + COUNTER_ATIVIDADES + "-atividade]")
  } else {
    atividade = document.querySelector("[id=id_atividade]")
  }

  if (document.querySelector("[id=id_meta_qualitativa]") === null) {
    meta_qualitativa = document.querySelector("[id=id_render_atividadesteletrabalho_periodo-" + COUNTER_ATIVIDADES + "-meta_qualitativa]")
  } else {
    meta_qualitativa = document.querySelector("[id=id_meta_qualitativa]")
  }

  if (tipo_meta_quantitativa = document.querySelector("[id=id_tipo_meta_quantitativa]") === null) {
    tipo_meta_quantitativa = document.querySelector("[id=id_render_atividadesteletrabalho_periodo-" + COUNTER_ATIVIDADES + "-tipo_meta_quantitativa]")
  } else {
    tipo_meta_quantitativa = document.querySelector("[id=id_tipo_meta_quantitativa]")
  }

  if (document.querySelector("[id=id_meta_quantitativa]") === null) {
    meta_quantitativa = document.querySelector("[id=id_render_atividadesteletrabalho_periodo-" + COUNTER_ATIVIDADES + "-meta_quantitativa]")
  } else {
    meta_quantitativa = document.querySelector("[id=id_meta_quantitativa]")
  }

  var inputValue = atividade.options[atividade.selectedIndex].innerText + ' - ' + meta_quantitativa.value + ' [' + tipo_meta_quantitativa.options[tipo_meta_quantitativa.selectedIndex].innerText + ']'

  if (atividade.value === '') {
    alert("Selecione uma atividade!")
    atividades = document.querySelectorAll("[id^='atividade-']")
    ultimo = atividades[atividades.length - 1].remove()
    return
  }

  if (tipo_meta_quantitativa.value === '') {
    alert("Selecione um tipo de meta quantitativa!")
    atividades = document.querySelectorAll("[id^='atividade-']")
    ultimo = atividades[atividades.length - 1].remove()
    return
  }

  if (meta_quantitativa.value === '') {
    alert("Selecione uma meta quantitativa!")
    atividades = document.querySelectorAll("[id^='atividade-']")
    ultimo = atividades[atividades.length - 1].remove()
    return
  }

  var t = document.createTextNode(inputValue)
  var a = document.createElement("a")
  a.setAttribute('count-atividade', COUNTER_ATIVIDADES)
  a.innerText = ' - [X]'

  a.addEventListener('click', function (ev) {
    li.remove()
    count_atividade = a.getAttribute('count-atividade')
    var atividade = document.getElementById("atividade-" + count_atividade)
    atividade.remove()
    reorderItems()
  })

  li.appendChild(t)
  li.appendChild(a)
  ul.appendChild(li)

  // criar o elemento com o atributo da COUNTER_ATIVIDADES, para depois criar uma função que remove o período
  COUNTER_ATIVIDADES++

  // reordena itens
  reorderItems_atividades()
}


function reorderItems_periodos() {
  // periodo
  Array.from(document.querySelectorAll("[id^='periodo-']"))
    .forEach((periodo, i) => {
      periodo.setAttribute('id', 'periodo-' + i)
      if (i >= 0) {
        // console.log(i)
        // console.log(periodo.querySelector('[type="hidden"]'))
        // console.log(periodo.querySelector('[data-field="data_inicio"]'))
        // console.log(periodo.querySelector('[data-field="data_fim"]'))

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
      if (i >= 0) {
        //console.log(periodo.querySelector('[data-field="periodo"]'))
        console.log(periodo.querySelector('[data-field="atividade"]'))
        console.log(periodo.querySelector('[data-field="meta_qualitativa"]'))
        console.log(periodo.querySelector('[data-field="tipo_meta_quantitativa"]'))
        console.log(periodo.querySelector('[data-field="meta_quantitativa"]'))

        //periodo.querySelector('[type="hidden"]').setAttribute('name', 'render_atividadesteletrabalho_periodo-' + i + '-' + 'periodo')
        periodo.querySelector('[data-field="atividade"]').setAttribute('name', 'render_atividadesteletrabalho_periodo-' + i + '-' + 'atividade')
        periodo.querySelector('[data-field="meta_qualitativa"]').setAttribute('name', 'render_atividadesteletrabalho_periodo-' + i + '-' + 'meta_qualitativa')
        periodo.querySelector('[data-field="tipo_meta_quantitativa"]').setAttribute('name', 'render_atividadesteletrabalho_periodo-' + i + '-' + 'tipo_meta_quantitativa')
        periodo.querySelector('[data-field="meta_quantitativa"]').setAttribute('name', 'render_atividadesteletrabalho_periodo-' + i + '-' + 'meta_quantitativa')

        //periodo.querySelector('[type="hidden"]').setAttribute('id', 'id_render_atividadesteletrabalho_periodo-' + i + '-' + 'periodo')
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