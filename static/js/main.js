// 等待DOM加载完成
$(document).ready(function() {
    // 初始化所有工具提示
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 初始化所有弹出框
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // 表格搜索功能
    $('#tableSearch').on('keyup', function() {
        var value = $(this).val().toLowerCase();
        $('.table tbody tr').filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
        });
    });

    // 表格排序功能
    $('.sortable').click(function() {
        var table = $(this).parents('table').eq(0);
        var rows = table.find('tr:gt(0)').toArray().sort(comparer($(this).index()));
        this.asc = !this.asc;
        if (!this.asc) rows = rows.reverse();
        for (var i = 0; i < rows.length; i++) table.append(rows[i]);
    });

    // 确认删除对话框
    $('.delete-confirm').click(function(e) {
        if (!confirm('确定要删除这条记录吗？')) {
            e.preventDefault();
        }
    });

    // 表单验证
    $('.needs-validation').submit(function(event) {
        if (!this.checkValidity()) {
            event.preventDefault();
            event.stopPropagation();
        }
        $(this).addClass('was-validated');
    });

    // 动态加载内容
    function loadContent(url, target) {
        $.ajax({
            url: url,
            method: 'GET',
            success: function(response) {
                $(target).html(response);
            },
            error: function(xhr, status, error) {
                console.error('加载失败:', error);
                $(target).html('<div class="alert alert-danger">加载失败</div>');
            }
        });
    }

    // 状态指示器更新
    function updateStatusIndicators() {
        $('.status-indicator').each(function() {
            var status = $(this).data('status');
            $(this).removeClass('status-online status-offline')
                   .addClass(status ? 'status-online' : 'status-offline');
        });
    }

    // 定期更新状态
    setInterval(updateStatusIndicators, 30000);

    // 图表初始化（如果页面中有图表）
    if (typeof Chart !== 'undefined' && $('#statusChart').length) {
        new Chart($('#statusChart'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: '设备状态',
                    data: [],
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

    // 辅助函数：表格排序比较器
    function comparer(index) {
        return function(a, b) {
            var valA = getCellValue(a, index), valB = getCellValue(b, index);
            return $.isNumeric(valA) && $.isNumeric(valB) ? valA - valB : valA.localeCompare(valB);
        };
    }

    function getCellValue(row, index) {
        return $(row).children('td').eq(index).text();
    }
}));