// search.js
document.querySelector('.search-button').addEventListener('click', function() {
    var searchValue = document.querySelector('.search-input').value;
    var resultsContainer = document.querySelector('.results-container');
    resultsContainer.innerHTML = '';

    fetch('/community_user_search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ search_query: searchValue })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('ネットワークレスポンスエラー');
        }
        return response.json();
    })
    .then(data => {
        if (data.length === 0) {
            let noResultMessage = document.createElement('div');
            noResultMessage.classList.add('no-result-message');
            noResultMessage.textContent = '検索結果が見つかりませんでした。';
            resultsContainer.appendChild(noResultMessage);
        } else {
            // 検索結果の処理
            data.forEach(user => {
                let resultItem = document.createElement('a');
                resultItem.classList.add('result-item');
                resultItem.href = `/user_detail/${user.user_id}`; // ユーザー詳細ページへのリンク
                
                // アイコンURLの生成
                let iconUrl = 'https://oshimore.s3.ap-northeast-1.amazonaws.com/img/';
                iconUrl += (user.icon_url && user.icon_url !== 'user_icon.png') ? user.icon_url : 'user_icon.png';

                resultItem.innerHTML = `
                    <div class="result-icon"><img src="${iconUrl}" alt="User Icon"></div>
                    <div class="result-name">${user.account_name}</div>
                    <div class="result-id">@${user.user_id}</div>
                `;
                resultsContainer.appendChild(resultItem);
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
        resultsContainer.textContent = 'エラーが発生しました。';
    });
});