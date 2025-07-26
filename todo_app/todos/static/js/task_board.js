document.addEventListener("DOMContentLoaded", function () {
  const rows = document.querySelectorAll("li[data-href]");
  rows.forEach((row) => {
    row.addEventListener("click", function () {
      window.location.href = this.dataset.href;
    });
  });
});

const STATUS = {
  notCompleted: "NOT_COMPLETED",
  progress: "PROGRESS",
  completed: "COMPLETED",
};

var notCompletedItems = document.getElementById("not-completed-items");
var progressItems = document.getElementById("progress-items");
var completedItems = document.getElementById("completed-items");

const getCookie = (name) => {
  if (document.cookie && document.cookie !== "") {
    for (const cookie of document.cookie.split(";")) {
      const [key, value] = cookie.trim().split("=");
      if (key === name) {
        return decodeURIComponent(value);
      }
    }
  }
};

const getTaskStatusByElemId = (elemId) => {
  if (elemId === "not-completed-items") {
    return STATUS.notCompleted;
  } else if (elemId === "progress-items") {
    return STATUS.progress;
  } else if (elemId === "completed-items") {
    return STATUS.completed;
  }
};

const updateTaskRequest = async (status, taskId, progress) => {
  const body = new URLSearchParams();
  body.append("taskId", taskId);
  body.append("status", status);
  if (progress !== undefined) {
    body.append("progress", progress);
  }
  const request = new Request("update", {
    method: "POST",
    body: body,
    headers: {
      "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
      "X-CSRFToken": getCookie("csrftoken"),
    },
  });

  await fetch(request);

  // --- 進捗率表示を即座に更新 ---
  if (progress !== undefined) {
    // D&Dで移動したli要素を取得
    const item = document.querySelector(`li.board-item[value="${taskId}"]`);
    if (item) {
      // 進捗率表示のspanを探す
      const progressSpan = item.querySelector(".progress-low, .progress-middle, .progress-high");
      if (progressSpan) {
        // クラスを更新
        progressSpan.classList.remove("progress-low", "progress-middle", "progress-high");
        if (progress <= 30) {
          progressSpan.classList.add("progress-low");
        } else if (progress <= 70) {
          progressSpan.classList.add("progress-middle");
        } else {
          progressSpan.classList.add("progress-high");
        }
        // 表示値を更新
        progressSpan.textContent = `${progress} %`;
      }
    }
  }
};

const getNewProgress = (fromStatus, toStatus) => {
  if (fromStatus === STATUS.notCompleted && toStatus === STATUS.progress) {
    return 10;
  }
  if (fromStatus === STATUS.progress && toStatus === STATUS.completed) {
    return 100;
  }
  if (fromStatus === STATUS.completed && (toStatus === STATUS.progress || toStatus === STATUS.notCompleted)) {
    return 0;
  }
  if (fromStatus === STATUS.progress && toStatus === STATUS.notCompleted) {
    return 0;
  }
  // それ以外は変更なし
  return undefined;
};

function removeDummyItem(list) {
  const dummy = list.querySelector('.dummy-item');
  if (dummy) dummy.remove();
}

function updateDummyItem(list) {
  const dummy = list.querySelector('.dummy-item');
  const items = list.querySelectorAll('.board-item:not(.dummy-item)');
  if (items.length > 0) {
    // タスクが1件以上ならdummy-itemを削除
    if (dummy) dummy.remove();
  } else {
    // タスクが0件ならdummy-itemがなければ追加
    if (!dummy) {
      const li = document.createElement('li');
      li.className = 'board-item dummy-item';
      li.setAttribute('value', '');
      li.style.minHeight = '48px';
      li.style.opacity = '0';
      li.style.pointerEvents = 'auto';
      li.innerHTML = `
        <div class="handle">
          <img src="/static/images/grip-vertical.svg" alt="handle">
        </div>
        <div class="v-line"></div>
        <div class="board-item-content">
          <div class="board-item-title"></div>
          <div class="board-item-description"></div>
          <div class="spacer"></div>
        </div>
      `;
      list.appendChild(li);
    }
  }
}

// 各リストのSortable初期化時にonAdd/onRemove/onUpdateで呼び出す
['not-completed-items', 'progress-items', 'completed-items'].forEach(id => {
  const el = document.getElementById(id);
  if (!el) return;
  new Sortable(el, {
    group: "shared",
    animation: 50,
    ghostClass: "blue-background-class",
    sort: true,
    onEnd: (e) => {
      const fromElemId = e.from.id;
      const toElemId = e.to.id;
      const taskId = e.item.value;
      const fromStatus = getTaskStatusByElemId(fromElemId);
      const toStatus = getTaskStatusByElemId(toElemId);
      if (fromStatus == toStatus) return;

      const newProgress = getNewProgress(fromStatus, toStatus);
      updateTaskRequest(toStatus, taskId, newProgress);
    },
    onAdd: function (evt) {
      removeDummyItem(evt.to);
      updateDummyItem(evt.to);
      updateDummyItem(evt.from);
    },
    onRemove: function (evt) {
      updateDummyItem(evt.from);
      updateDummyItem(evt.to);
    },
    onUpdate: function (evt) {
      updateDummyItem(evt.from);
      updateDummyItem(evt.to);
    },
  });
});
