(function () {
  var dataEl = document.getElementById('quiz-data');
  var root = document.getElementById('quiz');
  if (!dataEl || !root) return;

  var data = JSON.parse(dataEl.textContent);
  var keys = Object.keys(data);
  var tabs = document.createElement('div');
  tabs.className = 'tabs';
  var box = document.createElement('div');
  root.appendChild(tabs);
  root.appendChild(box);

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text) e.textContent = text;
    return e;
  }

  function show(key) {
    Array.prototype.forEach.call(tabs.children, function (b) {
      b.setAttribute('aria-pressed', b.dataset.key === key ? 'true' : 'false');
    });
    box.innerHTML = '';
    var quiz = data[key];
    var form = el('form');

    quiz.questions.forEach(function (q, qi) {
      var fs = el('fieldset');
      fs.appendChild(el('legend', '', (qi + 1) + '. ' + q.q));
      q.options.forEach(function (opt, oi) {
        var label = el('label');
        var input = document.createElement('input');
        input.type = 'radio';
        input.name = 'q' + qi;
        input.value = oi;
        label.appendChild(input);
        label.appendChild(document.createTextNode(' ' + opt));
        fs.appendChild(label);
      });
      form.appendChild(fs);
    });

    var btn = el('button', 'btn', 'Проверить');
    btn.type = 'submit';
    var reset = el('button', 'btn btn-ghost', 'Сбросить');
    reset.type = 'button';
    reset.addEventListener('click', function () { show(key); });
    var result = el('div', 'score');
    result.setAttribute('aria-live', 'polite');

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var score = 0;
      var fieldsets = form.querySelectorAll('fieldset');
      quiz.questions.forEach(function (q, qi) {
        var fs = fieldsets[qi];
        var old = fs.querySelector('.explain');
        if (old) old.remove();
        var chosen = form.querySelector('input[name="q' + qi + '"]:checked');
        var ok = chosen && Number(chosen.value) === q.answer;
        if (ok) score++;
        fs.className = ok ? 'ok' : 'bad';
        var msg = (ok ? 'Верно. ' : (chosen ? 'Неверно. ' : 'Нет ответа. ') + 'Правильный ответ: ' + q.options[q.answer] + '. ') + q.explain;
        fs.appendChild(el('p', 'explain', msg));
      });
      result.textContent = 'Результат: ' + score + ' из ' + quiz.questions.length;
    });

    form.appendChild(btn);
    form.appendChild(reset);
    form.appendChild(result);
    box.appendChild(form);
  }

  keys.forEach(function (key, i) {
    var b = el('button', '', data[key].name);
    b.type = 'button';
    b.dataset.key = key;
    b.addEventListener('click', function () { show(key); });
    tabs.appendChild(b);
  });
  show(keys[0]);
})();
