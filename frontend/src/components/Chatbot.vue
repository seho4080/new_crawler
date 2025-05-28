<script setup>
  import { ref, defineProps } from 'vue';

  const props = defineProps({
    articleId: {
      type: Number,
      required: true,
    }
  })

  const showChat = ref(false);
  const messages = ref([
    { author: 'bot', text: '안녕하세요 끼룩'}
  ]);
  const inputMessage = ref("");
  const arr = ['호에...?', '미안하지만 말해줄 수 없다 끼룩']
  const token = localStorage.getItem('access_token');
  const headers = token
    ? {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
    : {
      'Content-Type': 'application/json'
    }

  const sendMessage = async () => {
    messages.value.push({
      author: 'user', text: inputMessage.value
    })
    const message = inputMessage.value
    inputMessage.value = ""

    try {
      const response = await fetch(`http://localhost:8000/api/news/${props.articleId}/chat/`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
          "message": message
        })
      })

      if (response.ok) {
        const data = await response.json()
        
        messages.value.push({
          author: 'bot', text: data.message + " 끼룩"
        })
      } else {
        const randomItem = arr[Math.floor(Math.random() * arr.length)];
        messages.value.push({
          author: 'bot', text: randomItem
        })
        messages.value.push({
          author: 'bot', text: '다른거 뭐 도와드려요?'
        })
      }
    } catch (error) {
      console.log("Chatbot 요청 - ", error)
    }
  }

  const closeChat = () => {
    showChat.value = false;
  }

</script>

<template>
  <div class="chatbot-container">
    <div v-if="showChat" class="chatbot-bubble">
      <div class="chatbot-bubble__arrow"></div>
      <header class="chatbot-header">
        <h3>AI 비서 소봇</h3>
        <button class="close-btn" @click="closeChat">×</button>
      </header>
      <div class="chatbot-messages">
        <div
          v-for="(msg, i) in messages"
          :key="i"
          :class="['chatbot-message', msg.author]"
        >
          <span>{{ msg.text }}</span>
        </div>
      </div>
      <footer class="chatbot-input-area">
        <input
          v-model="inputMessage"
          @keyup.enter="sendMessage"
          placeholder="메시지를 입력하세요..."
        />
        <button @click="sendMessage">전송</button>
      </footer>
    </div>
    <div class="chatbot-emoji" @click="showChat = !showChat" title="채팅 열기">
      <img src="/chatbot.png" alt="Chatbot" />
    </div>
  </div>
</template>

<style scoped lang="scss">
.chatbot-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.chatbot-bubble {
  position: absolute;
  bottom: 100%;
  right: 0;
  width: 300px;
  height: 500px;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 15px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  margin-bottom: 8px;
}

.chatbot-bubble__arrow {
  position: absolute;
  bottom: -10px;
  right: 16px;
  width: 0;
  height: 0;
  border-left: 10px solid transparent;
  border-right:10px solid transparent;
  border-top: 10px solid #fff;
}

.chatbot-header {
  padding: 12px;
  background: #0c3057;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  .close-btn {
    background: transparent;
    border: none;
    color: white;
    font-size: 20px;
    cursor: pointer;
  }
}

.chatbot-messages {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  background: #f2f2f2;
  display: flex;
  flex-direction: column;
  .chatbot-message {
    display: inline-block;
    width: auto;
    white-space: pre-wrap;
    word-break: break-word;
    margin-bottom: 8px;
    padding: 8px 12px;
    border-radius: 16px;

    &.bot {
      background: #ffffff;
      align-self: flex-start;
    }
    &.user {
      background: #0c3057;
      color: white;
      align-self: flex-end;
    }
  }
}

.chatbot-input-area {
  display: flex;
  padding: 8px;
  border-top: 1px solid #ddd;
  input {
    flex: 1;
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 16px;
    outline: none;
  }
  button {
    margin-left: 8px;
    padding: 8px 12px;
    background: #0c3057;
    color: white;
    border: none;
    border-radius: 16px;
    cursor: pointer;
  }
}

.chatbot-emoji {
  width: 56px;
  height: 56px;
  cursor: pointer;
  img {
    width: 100%;
    height: 100%;
    border-radius: 100%;
  }
}
</style>
