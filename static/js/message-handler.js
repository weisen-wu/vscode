// 引入SweetAlert2库
document.addEventListener('DOMContentLoaded', function() {
    // 获取所有flash消息
    const flashMessages = document.querySelectorAll('.alert');
    
    // 如果存在flash消息，使用SweetAlert2显示
    if (flashMessages.length > 0) {
        flashMessages.forEach(function(flashMessage) {
            const message = flashMessage.textContent.trim();
            // 移除原始的flash消息元素
            flashMessage.remove();
            
            // 使用SweetAlert2显示消息
            Swal.fire({
                title: '操作提示',
                text: message,
                icon: 'info',
                confirmButtonText: '确定',
                confirmButtonColor: '#3085d6'
            });
        });
    }
    
    // 处理删除确认
    document.addEventListener('click', function(e) {
        if (e.target && e.target.matches('button[type="submit"]')) {
            const deleteForm = e.target.closest('form[action*="delete"]');
            if (deleteForm) {
                e.preventDefault();
                
                Swal.fire({
                    title: '确认删除',
                    text: '您确定要删除这条记录吗？',
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonColor: '#d33',
                    cancelButtonColor: '#3085d6',
                    confirmButtonText: '确定删除',
                    cancelButtonText: '取消'
                }).then((result) => {
                    if (result.isConfirmed) {
                        deleteForm.submit();
                    }
                });
            }
        }
    });
});