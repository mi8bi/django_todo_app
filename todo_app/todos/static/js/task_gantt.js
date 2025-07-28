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

const getTasksRequest = async (url) => {
  try {
    const response = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
    });
    if (!response.ok) {
      if (response.status === 404) {
        throw new Error(`${response.status} Resource not found: ${url}`);
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error("Fetch error:", error);
    throw error;
  }
};

window.onload = async () => {
  // タスクを用意
  const tasks = await getTasksRequest("get");
  const ganttData = tasks.map((task) => {
    return {
      id: task.id,
      name: task.title,
      description: task.description,
      start: task.start_date,
      end: task.due_date,
      progress: task.progress,
    };
  });

  // gantt をセットアップ
  const gantt = new Gantt("#gantt", ganttData, {
    // ダブルクリック時
    on_click: (task) => {
      console.log(task.description);
    },
    // 日付変更時
    on_date_change: (task, start, end) => {
      console.log(`${task.name}: change date`);
    },
    // 進捗変更時
    on_progress_change: (task, progress) => {
      console.log(`${task.name}: change progress to ${progress}%`);
    },
    view_mode: 'Week',
  });

  const viewModeSelect = document.getElementById('gantt-view-mode');
  viewModeSelect.addEventListener('change', () => {
    gantt.change_view_mode(viewModeSelect.value);
  });
};
