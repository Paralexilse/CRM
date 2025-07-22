const socket = io();
const currentUserId = window.CURRENT_USER_ID;
const departmentId = window.DEPARTMENT_ID;
    
    // Подключаемся к комнате
socket.emit('join_department', { department_id: departmentId });
    
    // Отправка сообщения
document.querySelector('form').addEventListener('submit', function(e) {
    e.preventDefault();
    const messageInput = this.querySelector('input[name="message"]');
    const message = messageInput.value.trim();

    if (message) {
        socket.emit('send_message_department', {
            sender_id: currentUserId,
            department_id: departmentId,
            message: message
        });
        messageInput.value = '';
    }
});
    
    // Получение сообщения
// socket.on('receive_message', function(data) {
//     const messagesContainer = document.querySelector('#messages-container');
//     const messageElement = document.createElement('p');
//     messageElement.textContent = `${data.firts_name} ${data.last_name} - ${data.message} - ${data.datetime} `;
//     messagesContainer.appendChild(messageElement);
// });
socket.on('receive_message_department', function(data) {
    const messagesContainer = document.querySelector('#messages-container');
    const messageElement = document.createElement('p');
    
    // Генерируем URL аватарки на клиенте
    const avatarUrl = `/user/user_avatar${data.sender_id}`;  // Предполагаемый маршрут
    
    messageElement.innerHTML = `
        <img style="max-width: 100px; max-height: 100px;" 
             src="${avatarUrl}" 
             alt="${data.first_name} ${data.last_name}">
        ${data.first_name} ${data.last_name} - ${data.message} - ${data.datetime}
    `;
    
    messagesContainer.appendChild(messageElement);
});