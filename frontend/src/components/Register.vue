<script setup>
  import { ref } from 'vue';
  import { useRouter } from 'vue-router';
  
  const username = ref('')
  const email = ref('')
  const password = ref('')
  const errorMessage = ref('')
  const router = useRouter();
  
  const handleRegister = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/api/members/signup/", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: username.value,
          email: email.value,
          password: password.value,
        }),
      })
        .then(response => {
          if (response.status === 201) {
            alert("회원 가입 성공 !")
            router.replace("/login")
          }
          else {
            alert("회원 가입 실패 !")
          }
        })
    }
    catch (error) {
      console.log("error 발생, " + error)
    }
  }

</script>

<template>
  <div class="register-container">
    <form @submit.prevent="handleRegister">
      <input 
        type="text" 
        v-model="username" 
        placeholder="name" 
        required
      />
      <input
        type="email"
        v-model="email"
        placeholder="e-mail"
        required
      />
      <input
        type="password"
        v-model="password"
        placeholder="password"
        required
      />
      <button type="submit">회원가입</button>
      <p class="error" v-if="errorMessage">{{ errorMessage }}</p>
    </form>
  </div>
</template>

<style scoped>
/* 회원가입 카드 */
.register-container {
  max-width: 360px;
  margin: 80px auto;
  padding: 2rem;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  font-family: 'Noto Sans KR', sans-serif;
}

/* 내부 레이아웃 */
.register-container form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* 입력창 스타일 */
.register-container input {
  padding: 0.75rem 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 1rem;
  color: #333333;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.register-container input:focus {
  outline: none;
  border-color: #001f3f;
  box-shadow: 0 0 0 2px rgba(0, 31, 63, 0.2);
}

/* 회원가입 버튼 */
.register-container button[type="submit"] {
  background-color: #001f3f;
  color: #ffffff;
  padding: 0.75rem;
  font-size: 1rem;
  font-weight: 500;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.register-container button[type="submit"]:hover {
  background-color: #003060;
}

/* 에러 메시지 */
.register-container .error {
  color: #e53935;
  font-size: 0.875rem;
  margin-top: -0.5rem;
  text-align: center;
}
</style>
