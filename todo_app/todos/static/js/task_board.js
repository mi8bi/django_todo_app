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

const updateTaskRequest = async (status, taskId) => {
  const body = new URLSearchParams();
  body.append("taskId", taskId);
  body.append("status", status);
  const request = new Request("update", {
    method: "POST",
    body: body,
    headers: {
      "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
      "X-CSRFToken": getCookie("csrftoken"),
    },
  });

  await fetch(request);
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

      updateTaskRequest(toStatus, taskId);
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

      updateTaskRequest(toStatus, taskId);
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

      updateTaskRequest(toStatus, taskId);
    },
  });
}
