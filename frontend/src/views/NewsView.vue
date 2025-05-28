<script setup>
  import { ref, onMounted, watch } from "vue";
  import ContentBox from "@/common/ContentBox.vue";
  import NewsCard from "@/components/NewsCard.vue";
  import { tabs } from "@/assets/data/tabs";
  import PaginationButton from "@/common/PaginationButton.vue";
  import StateButton from "@/common/StateButton.vue";

  const sortBy = ref("latest");
  const newsList = ref([]);
  const activeTab = ref(tabs[0].id);
  const currentPage = ref(1);
  const totalPages = ref(1);
  const itemsPerPage = 10;
  const newsData = ref([]);

  const getNews = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/news/", {
        method: "GET",
      })

      if (response.ok) {
        const data = await response.json();
        newsData.value = Array.from({ length: tabs.length }, () => ({
          rawData: [],
          latest: [],
          recommend: [],
          totalPageValue: 0
        }));

        const keys = Object.keys(data)

        // 키워드 별 기사 처리 로직
        keys.forEach((key, idx) => {
          const items = data[key]

          items.forEach(item => {
            newsData.value[0].rawData.push(item)
            newsData.value[idx+1].rawData.push(item)
          })

          const latest = [...newsData.value[idx+1].rawData].sort((a, b) => b.write_date - a.write_date)
          const latestChunk = []
          const recommend = [...newsData.value[idx+1].rawData].sort((a, b) => b.total_like - a.total_like)  
          const recommendChunk = []

          for (let i = 0; i < latest.length; i += itemsPerPage) {
            latestChunk.push(latest.slice(i, i + itemsPerPage));
          }

          for (let i = 0; i < recommend.length; i += itemsPerPage) {
            recommendChunk.push(recommend.slice(i, i + itemsPerPage));
          }

          newsData.value[idx+1].latest = latestChunk
          newsData.value[idx+1].recommend = recommendChunk
          newsData.value[idx+1].totalPageValue = recommendChunk.length
        })

        // 전체 기사 처리 로직
        const latest = [...newsData.value[0].rawData].sort((a, b) => b.write_date - a.write_date)
        const latestChunk = []
        const recommend = [...newsData.value[0].rawData].sort((a, b) => b.total_like - a.total_like)  
        const recommendChunk = []

        for (let i = 0; i < latest.length; i += itemsPerPage) {
          latestChunk.push(latest.slice(i, i + itemsPerPage));
        }

        for (let i = 0; i < recommend.length; i += itemsPerPage) {
          recommendChunk.push(recommend.slice(i, i + itemsPerPage));
        }

        newsData.value[0].latest = latestChunk
        newsData.value[0].recommend = recommendChunk
        newsData.value[0].totalPageValue = latestChunk.length

        newsList.value = latestChunk
        totalPages.value = latestChunk.length
      } else {
        console.log("뉴스 데이터를 불러오지 못했습니다")
      }
    } catch (error) {
      console.log(error)
    }
  };

  const changeArticles = () => {
    if (sortBy.value === 'latest') {
      newsList.value = newsData.value[activeTab.value-1].latest
      totalPages.value = newsData.value[activeTab.value-1].totalPageValue
    }
    else {
      newsList.value = newsData.value[activeTab.value-1].recommend
      totalPages.value = newsData.value[activeTab.value-1].totalPageValue
    }
    currentPage.value = 1
  }

  const handleClickCategoryButton = (id) => {
    activeTab.value = id
    if (sortBy === 'latest') {
      newsList.value = newsData.value[activeTab.value-1].latest
    } else {
      newsList.value = newsData.value[activeTab.value-1].recommend
    }
    totalPages.value = newsData.value[activeTab.value-1].totalPageValue
    currentPage.value = 1
  }

  onMounted(() => {
    getNews();
  });

  watch([sortBy, activeTab], () => {
    changeArticles();
  }, {immediate: false})
</script>

<template>
  <div class="news">
    <div>
      <h1 class="news__title">🤖 AI 맞춤 추천 뉴스</h1>
      <p class="news__description">
        당신이 원하는 뉴스, 이제 AI가 직접 추천해드립니다!<br />
        나만의 취향을 기반으로, 맞춤형 뉴스만 쏙쏙 골라주는<br />
        뉴스 큐레이팅 서비스
        <strong style="font-weight: bold">SSAFYNEWS</strong>에 빠져보세요.
        <br />AI 챗봇과 기사에 대해 대화하며 궁금한 점을 물어보고, <br />한눈에
        보기 쉬운 대시보드를 통해 나의 뉴스 소비 패턴도 확인할 수 있습니다.
      </p>

      <ContentBox class="news__tabs">
        <StateButton
          v-for="tab in tabs"
          :key="tab.id"
          type="state"  
          :is-active="activeTab === tab.id"
          @click="handleClickCategoryButton(tab.id)"
        >
          {{ tab.label }}
        </StateButton>
      </ContentBox>
    </div>
    <ContentBox class="news__box">
      <div class="news__box__title-container">
        <div class="filters__container">
          <select class="filters" v-model="sortBy">
            <option value="latest">최신순</option>
            <option value="recommend">추천순</option>
          </select>
        </div>
      </div>

      <!-- <div class="news__box__cards" v-for="news in newsList[currentPage.value-1]" :key="news.id">
        <NewsCard :data="news" />
      </div> -->
      <div v-if="newsList.length && newsList[currentPage-1]" class="news__box__cards">
        <div v-for="news in newsList[currentPage-1]" :key="news.article_id">
          <NewsCard :data="news" />
        </div>
      </div>

      <PaginationButton v-model="currentPage" :totalPages="totalPages" />
    </ContentBox>
  </div>
</template>

<style scoped lang="scss">
.news {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: 30px;
  justify-content: center;

  &__title {
    font-size: 20px;
    font-weight: 700;
    border-bottom: 1px solid #e2e2e2;
    padding-bottom: 10px;
  }

  &__description {
    font-size: 16px;
    font-weight: 400;
    color: #575757;
    line-height: normal;
    margin: 15px 0 25px;

    &--job {
      color: red;
      margin-bottom: 20px;
    }
  }

  &__tabs {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    padding: 12px 30px !important;
  }

  &__box {
    padding: 30px !important;

    &__noti {
      color: #666666;
      font-size: 12px;
      padding: 5px 10px;
    }

    &__title-container {
      position: relative;
      display: flex;
      align-items: center;
    }

    &__title {
      font-weight: 700;
      font-size: 21px;
      cursor: pointer;

      &-username {
        font-weight: 400;
        padding: 3px;
        border-bottom: 2px solid #272c97;
      }
      &-icon {
        font-size: 15px;
      }
    }

    &__subtitle-loggedin {
      font-weight: 400;
      padding: 10px 0 0 10px;
      color: #575757;
      opacity: 0;
      transition: opacity 0.3s ease;
      pointer-events: none;
      text-decoration: underline;
    }

    &__title-container:hover .news__box__subtitle-loggedin {
      opacity: 1;
    }

    .filters__container {
      position: absolute;
      right: 0;
    }

    &__cards {
      margin-top: 30px;
      margin-left: 30px;
    }
  } 
}
</style>
