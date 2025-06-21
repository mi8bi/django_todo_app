document.addEventListener("DOMContentLoaded", function () {
  const rows = document.querySelectorAll("td[data-href]");
  rows.forEach((row) => {
    row.addEventListener("click", function () {
      window.location.href = this.dataset.href;
    });
  });

  const checkboxes = document.querySelectorAll('input[type="checkbox"]');
  checkboxes.forEach((checkbox) => {
    checkbox.addEventListener("click", function (event) {
      event.stopPropagation();
    });
  });
});

const checkall = document.getElementById("checksAll");
const checks = document.querySelectorAll(".checks");
// 全て選択のチェックボックスがクリックされた時
checkall.addEventListener("click", () => {
  for (val of checks) {
    checkall.checked == true ? (val.checked = true) : (val.checked = false);
  }
});
// 個別のチェックボックスがクリックされた時
checks.forEach((element) => {
  element.addEventListener("click", () => {
    // チェックが1つでも外された時
    if (element.checked == false) {
      checkall.checked = false;
    }
    // 全てにチェックがされた時
    if (document.querySelectorAll(".checks:checked").length == checks.length) {
      checkall.checked = true;
    }
  });
});
