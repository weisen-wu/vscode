// WebSocket连接管理
let ws = null;
const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsUrl = `${wsProtocol}//${window.location.host}/ws/estatione`;

// 更新连接状态显示
function updateConnectionStatus(status, message) {
    const statusBar = document.getElementById('connection-status');
    if (!statusBar) return;
    
    statusBar.textContent = message;
    statusBar.className = `connection-status ${status}`;
}

// 初始化WebSocket连接
function initWebSocket() {
    updateConnectionStatus('connecting', '正在连接...');
    
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log('WebSocket连接已建立');
        updateConnectionStatus('connected', '已连接');
        // 连接成功后定期发送心跳包
        setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ type: 'ping' }));
            }
        }, 5000);
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        updateDeviceStatus(data);
    };

    ws.onclose = () => {
        console.log('WebSocket连接已关闭，尝试重新连接...');
        updateConnectionStatus('disconnected', '连接已断开，正在重新连接...');
        setTimeout(initWebSocket, 5000);
    };

    ws.onerror = (error) => {
        console.error('WebSocket错误:', error);
        updateConnectionStatus('error', '连接出错');
    };
}

// 更新设备状态显示
function updateDeviceStatus(data) {
    const deviceRow = document.querySelector(`tr[data-device-id="${data.mac_id}"]`);
    if (!deviceRow) return;

    const statusCell = deviceRow.querySelector('.device-status');
    const lastConnectedCell = deviceRow.querySelector('.last-connected');
    const statusIndicator = statusCell.querySelector('.status-indicator');

    // 更新状态指示器
    statusIndicator.classList.remove('status-connected', 'status-disconnected');
    statusIndicator.classList.add(data.connected ? 'status-connected' : 'status-disconnected');
    statusCell.querySelector('.status-text').textContent = data.connected ? '在线' : '离线';

    // 更新最后连接时间
    if (data.last_connected) {
        lastConnectedCell.textContent = new Date(data.last_connected).toLocaleString('zh-CN');
    }
}

// 确保DOM完全加载后再初始化WebSocket
window.addEventListener('load', () => {
    // 等待一小段时间确保所有资源都已加载完成
    setTimeout(() => {
        initWebSocket();
    }, 500);
});