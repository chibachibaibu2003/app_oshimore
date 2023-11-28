// search.js
document.querySelector('.search-button').addEventListener('click', function() {
    var searchValue = document.querySelector('.search-input').value;
    var resultsContainer = document.querySelector('.results-container');
    resultsContainer.innerHTML = '';

    document.querySelector('.search-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            executeSearch();
        }
    });

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
                resultItem.innerHTML = `
                    <div class="result-icon"><img src="${user.icon_url || 'default_icon.png'}"></div>
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