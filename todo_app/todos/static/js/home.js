document.addEventListener("DOMContentLoaded", async function () {
  const GRAPH_COLORS = [
    "#ef5350",
    "#64b5f6",
    "#ffee58",
    "#66bb6a",
    "#ab47bc",
    "#259b24",
    "#8bc34a",
    "#ffeb3b",
    "#ffc107",
    "#ff9800",
    "#73f4aa",
    "#39dc99",
    "#39cedc",
    "	#397cdc",
    "#7cdc39",
    "#cddc39",
  ];

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

  const getChartData = async (url) => {
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

  const aggregateTasksByCategory = (tasks) => {
    const categoryCounts = {};

    tasks.forEach((task) => {
      const category = task.category_title;
      if (categoryCounts[category]) {
        categoryCounts[category]++;
      } else {
        categoryCounts[category] = 1;
      }
    });

    return categoryCounts;
  };

  const getRandomColors = (colorCount) => {
    const colors = [];
    const graph_colors = [...GRAPH_COLORS];
    for (let i = 0; i < colorCount; i++) {
      const r = Math.floor(Math.random() * graph_colors.length);
      colors.push(graph_colors[r]);
      graph_colors.splice(r, 1);
    }
    return colors;
  };

  const chartData = await getChartData("/todos/home/bar-chart");
  const categories = aggregateTasksByCategory(chartData);

  const barElement = document.getElementById("bar-chart");
  const doughnutElement = document.getElementById("doughnut-chart");

  // 棒グラフ
  new Chart(barElement, {
    type: "bar",
    data: {
      labels: Object.keys(categories),
      datasets: [
        {
          label: "Catetory",
          data: Object.values(categories),
          borderWidth: 1,
          backgroundColor: ["#009879"],
        },
      ],
    },
    options: {
      plugins: {
        legend: {
          position: "right",
        },
      },
      scales: {
        y: {
          grace: "10%", // 余白
          beginAtZero: true,
        },
      },
      maintainAspectRatio: false, // レスポンシブ
    },
  });

  // 円グラフ
  new Chart(doughnutElement, {
    type: "doughnut",
    data: {
      labels: Object.keys(categories),
      datasets: [
        {
          label: "Catetory",
          data: Object.values(categories),
          borderWidth: 1,
          backgroundColor: getRandomColors(Object.values(categories).length),
        },
      ],
    },
    options: {
      plugins: {
        legend: {
          position: "right",
        },
      },
      scales: {
        y: {
          grace: "10%", // 余白
          beginAtZero: true,
        },
      },
      maintainAspectRatio: false, // レスポンシブ
    },
  });
});
