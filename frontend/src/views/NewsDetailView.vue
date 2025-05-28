<script setup>
  import { onMounted, ref } from "vue";
  import ContentBox from "@/common/ContentBox.vue";
  import StateButton from "@/common/StateButton.vue";
  import { useDate } from "@/composables/useDate";
  import router from "@/router";
  import LeftArrow from "@/components/icon/LeftArrow.svg";
  import ArticlePreview from "@/components/ArticlePreview.vue";
  import { useRoute } from 'vue-router';
  import CommentBox from "@/components/CommentBox.vue";
  import Chatbot from "@/components/Chatbot.vue";

  const news = ref();
  const route = useRoute();
  const articleId = route.params.id;
  const likeCount = ref(0);
  const liked = ref(false);
  const isAnimating = ref(false);
  const relatedNews = ref([]);
  const comments = ref([]);
  const newComment = ref('');
  const token = localStorage.getItem("access_token")
  const headers = token
    ? {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
    : {
      'Content-Type': 'application/json'
    }

  const getDetailNews = async () => {
    try {
      const res = await fetch(`http://localhost:8000/api/news/${articleId}/`, {
        method: "GET",
        headers: headers,
      })

      if (res.ok) {
        const data = await res.json()

        news.value = data
        console.log(news.value)
        likeCount.value = data.total_like
        liked.value = data.is_like
      }
    } catch (error) {
      console.log(error)
    }
  }

  const getRelatedNews = async () => {
    try {
      const response = await fetch( `http://localhost:8000/api/news/${articleId}/similar/`, {
        method: "GET",
      })
      
      if (response.ok) {
        const data = await response.json()

        relatedNews.value = data.article_list
      }
    } catch (error) {
      console.log(error)
    }
  }

  const getComment = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/news/comment/${articleId}/`, {
        method: 'GET',
      })

      if (response.ok) {
        comments.value = await response.json()
      } else {
        console.log("comment load error - response status code: ", response.status)
      }
    } catch (error) {
      console.log(error)
    }
  }

  const postComment = async () => {
    const content = newComment.value.trim()
    if (!content) return

    try {
      const res = await fetch(`http://localhost:8000/api/news/comment/${articleId}/`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
          "content": content
        })
      })
      if (!res.ok) throw new Error()
      const data = await res.json()
      comments.value = [data, ...comments.value]

      newComment.value = ''
    } catch {
      alert('댓글 작성에 실패했습니다.')
    }
  }

  const handleClickLike = () => {
    if (!liked.value) {
      likeCount.value = likeCount.value + 1;
      liked.value = true;
      
      try {
        fetch(`http://localhost:8000/api/news/${articleId}/likes/`, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          }
        })
      } catch (error) {
        liked.value = false
        console.log("error, " + error)
      }
    } else {
      likeCount.value = likeCount.value - 1;
      liked.value = false

      try {
        fetch(`http://localhost:8000/api/news/${articleId}/likes/`, {
          method: 'DELETE', 
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          }
        })
      } catch (error) {
        liked.value = true
        console.log("error, " + error)
      }
    }
  };

  const { formatDate } = useDate();

  onMounted(() => {
    getDetailNews();
    getRelatedNews();
    getComment();
  })
</script>

<template>
  <button @click="() => router.back()" class="back-btn">
    <img :src="LeftArrow" alt ="뒤로 가기" />
  </button>
  <div v-if="news" class="news-detail">
    <div class="article__container">
      <ContentBox>
        <div class="article">
          <div class="article__header">
            <StateButton type="state" size="sm" isActive disabled>{{
              news?.category
            }}</StateButton>
            <h2 class="article__header-title">{{ news?.title }}</h2>
            <div class="article__header-writer">
              <span>{{ news.writer }}</span>
              <span> 🕒 {{ formatDate(news.write_date) }}</span>
            </div>
          </div>

          <p class="article__content">{{ news?.content }}</p>

          <div class="article__tags">
            <StateButton
              v-for="(tag, index) in news.keywords"
              :key="index"
              type="tag"
              size="sm"
            >
              {{ tag }}
            </StateButton>
          </div>

          <div class="article__content__footer">
            <div class="article__content__emoji">
              <span class="emoji-btn">
                <span v-if="liked"> ❤️ </span> <span v-else>🤍</span
                >{{ likeCount }}
              </span>
              <div class="emoji-btn">
                <span class="content__emoji-eye"> 👀 </span
                >{{ news?.total_read }}
              </div>

              <a :href="news.url">📄</a>
            </div>
            <button class="emoji-btn" @click="handleClickLike">
              <span>{{ liked ? "❤️" : "🤍" }} 좋아요</span>
            </button>
            <!-- 애니메이션 하트 -->
            <transition name="heart-float">
              <span v-if="isAnimating" class="floating-heart">
                {{ liked ? "❤️" : "🤍" }}
              </span>
            </transition>
          </div>
        </div>
      </ContentBox>
      <ContentBox>
        <div class="add-comment-container">
          <div class="comment-input">
            <textarea v-model="newComment" placeholder="댓글 추가..." class="comment-box" rows="1"></textarea>
          </div>
          <div class="add-comment-button-container">
            <button class="btn-comment" :disabled="!newComment.trim()" @click="postComment">댓글</button>
          </div>
        </div>
        <div v-if="comments && comments.length > 0">
          <div v-for="(comment, index) in comments" :key="index">
            <CommentBox :data="comment" />
          </div>
        </div>
        <div v-else class="no-comment">
            <h4>아직 댓글이 없습니다.</h4>
        </div>
      </ContentBox>
    </div>

    <ContentBox class="sidebar">
      <h1 class="sidebar__title">📰 관련 기사</h1>
      <div v-for="(news, index) in relatedNews" :key="index">
        <ArticlePreview :to="`/news/${news.article_id}`" :news="news" />
      </div>
    </ContentBox>
    <Chatbot :articleId="articleId"/>
  </div>
</template>

<style scoped lang="scss">
.back-btn {
  margin-bottom: 10px;
}

.news-detail {
  display: flex;
  gap: 20px;

  @media (max-width: 800px) {
    flex-direction: column;
  }

  .article__container {
    flex: 2;
    display: flex;
    flex-direction: column;
    gap: 50px;
  }

  .sidebar {
    flex: 1;
    &__title {
      font-weight: 700;
      font-size: 18px;
      margin-bottom: 20px;
    }
  }

  .comment-box::placeholder {
    color: #999;         /* 유튜브처럼 연한 회색 */
    font-weight: 550;    /* 보통(bold 정도로 느껴질 만한 중간 값) */
    font-size: 0.9rem;     /* 필요하다면 크기도 조절 */
  }

  .add-comment-button-container {
    margin-top: 5px;
    display: flex;
    flex-direction: row-reverse;
  }

  .no-comment {
    display: flex;
    justify-content: center;
  }

  .article {
    font-size: 1rem;
    padding: 20px;
    &__header {
      color: #888;
      font-size: 0.9rem;
      margin-bottom: 10px;
      &-title {
        margin: 12px 0;
        font-size: 1.6rem;
        font-weight: bold;
        color: #1c1c1e;
      }
      &-writer {
        display: flex;
        gap: 10px;
      }
    }

    &__content {
      margin: 16px 0;
      line-height: 1.6;

      &__footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 30px;
      }

      &__emoji {
        color: #888;
        font-size: 16px;
        display: flex;
        gap: 30px;
        align-items: center;
        &-eye {
          font-size: 17px;
        }
      }
    }

    &__tags {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-top: 15px;
    }
  }

  .comment-box {
    flex: 1;
    border: none;
    border-bottom: 1px solid #ccc;
    resize: none;
    padding: 4px;
  }

  .btn-comment {
    background-color: #0c3057;
    color: #fff;
    border: none;
    padding: 6px 12px;
    border-radius: 16px;
    cursor: pointer;
  }

  .btn-comment:disabled {
    background-color: #ccc;
    cursor: default;
  }

  .emoji-btn {
    display: flex;
    align-items: center;
    font-size: 15px;
    color: #888;
    cursor: pointer;
  }

  .floating-heart {
    position: absolute;
    font-size: 24px;
    color: red;
    animation: heartFloat 0.6s ease-out forwards;
  }

  @keyframes heartFloat {
    0% {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
    50% {
      opacity: 0.8;
      transform: translateY(-20px) scale(1.2);
    }
    100% {
      opacity: 0;
      transform: translateY(-40px) scale(0.8);
    }
  }
}

.comment-input {
  padding: 5px;
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  border-bottom: 1px solid #ccc;
}

.comment-input .comment-box {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  padding: 4px 0;
}

.comment-input::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 0;
  height: 2px;
  background: black;
  transition: width 0.3s ease, left 0.3s ease;
}

.comment-input:focus-within::after {
  left: 0;
  width: 100%;
}
</style>