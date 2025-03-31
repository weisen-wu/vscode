// 统一的对话框处理函数
function confirmDelete(url, message) {
    Swal.fire({
        title: '确认删除',
        text: message,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d',
        confirmButtonText: '确定删除',
        cancelButtonText: '取消'
    }).then((result) => {
        if (result.isConfirmed) {
            // 创建一个表单来提交删除请求
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = url;
            document.body.appendChild(form);
            form.submit();
        }
    });
    return false;
}

// 显示操作成功消息
function showSuccess(message) {
    Swal.fire({
        title: '成功',
        text: message,
        icon: 'success',
        timer: 2000,
        showConfirmButton: false
    });
}

// 显示操作失败消息
function showError(message) {
    Swal.fire({
        title: '错误',
        text: message,
        icon: 'error'
    });
}

// 处理Flash消息
document.addEventListener('DOMContentLoaded', function() {
    const messageContainer = document.getElementById('message-container');
    if (messageContainer) {
        const messages = messageContainer.dataset.messages;
        if (messages) {
            try {
                const parsedMessages = JSON.parse(messages);
                parsedMessages.forEach(msg => {
                    if (msg.category === 'success') {
                        showSuccess(msg.message);
                    } else if (msg.category === 'error') {
                        showError(msg.message);
                    }
                });
            } catch (e) {
                console.error('Error parsing messages:', e);
            }
        }
    }
});