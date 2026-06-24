# ytac-models — archived

The ORM models previously in this package have been merged into [ytac](https://github.com/altCensored/ytac).

Update your dependency:

```toml
# before
"ytac-models@git+https://github.com/altCensored/ytac-models"

# after
"ytac@git+https://github.com/altCensored/ytac"
```

Update your imports:

```python
# before
from ytac_models.db import Video, Source, Base

# after
from ytac.db import Video, Source, Base
```
