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

if (notCompletedItems) {
  new Sortable(notCompletedItems, {
    group: "shared",
    animation: 150,
    handle: ".handle",
    ghostClass: "blue-background-class",
    sort: false,
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
  });
}

if (progressItems) {
  new Sortable(progressItems, {
    group: "shared",
    animation: 150,
    handle: ".handle",
    ghostClass: "blue-background-class",
    sort: false,
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
  });
}

if (completedItems) {
  new Sortable(completedItems, {
    group: "shared",
    animation: 150,
    handle: ".handle",
    ghostClass: "blue-background-class",
    sort: false,
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
  });
}
