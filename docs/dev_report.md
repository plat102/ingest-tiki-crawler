# Project 02: Thu thập dữ liệu sản phẩm Tiki

> DoD: Sử dụng code Python, tải về thông tin của 200k sản phẩm (list product id bên dưới) của Tiki và lưu thành các file .json. Mỗi file có thông tin của khoảng 1000 sản phẩm. Các thông in cần lấy bao gồm: id, name, url_key, price, description, images url. Yêu cầu chuẩn hoá nội dung trong "description" và tìm phương án rút ngắn thời gian lấy dữ liệu.
> <br> List product_id: [https://1drv.ms/u/s!AukvlU4z92FZgp4xIlzQ4giHVa5Lpw?e=qDXctn](https://1drv.ms/u/s!AukvlU4z92FZgp4xIlzQ4giHVa5Lpw?e=qDXctn)
> <br> API get product detail: [https://api.tiki.vn/product-detail/api/v1/products/138083218](https://api.tiki.vn/product-detail/api/v1/products/138083218)
> <br> Lưu ý: Cần lưu lại những sản phẩm bị lỗi và lý do lỗi.
> <br> Tổng quan về json có thể tham khảo tại đây: [https://www.youtube.com/watch?v=iiADhChRriM](https://www.youtube.com/watch?v=iiADhChRriM)
> <br> Link submit project sau khi hoàn thành: [https://docs.google.com/forms/d/1iIJavuPT7haom8NQSGiBwD-d8nMKeAGCBtXvZEEtH_A/edit](https://docs.google.com/forms/d/1iIJavuPT7haom8NQSGiBwD-d8nMKeAGCBtXvZEEtH_A/edit)

## Phân tích yêu cầu


| Input              | Output                                                    |
| ------------------ | --------------------------------------------------------- |
| 200000 product ids | ~ 200 files (1000 sp / file)                              |
| .csv               | .json (id, name, url_key, price, description, images url) |

Constraints:

1. Chuẩn hóa description
2. Tối ưu thời gian crawl
3. Log lỗi chi tiết

Questions:

- Nguồn data? -> API từng sp
- 200k request dự kiến gọi tuần tự mất bao lâu? -> 12 tiếng
- Làm sao nhanh hơn? -> Gọi song song nhiều request vì data k phụ thuộc vào nhau
  - Các cách gọi song song?
- Nếu gặp lỗi?
  - Dừng: Checkpoint -> resume
  - 1 prod: Log lỗi -> skip (product lỗi + product có data = tổng?)

### Data flow

```txt
CSV -> checkpoint -> async crawl theo từng batch -> Update checkpoint

Trong mỗi batch:
- Call API async concurrent
- Parse response, clean description
- Save to JSON
- Update checkpoint
```

## Common Issues


| Issue                   | Mô tả                      | Cause                                                                    | Solution                                                                                    |
| :---------------------- | :--------------------------- | :----------------------------------------------------------------------- | :------------------------------------------------------------------------------------------ |
| **Rate Limiting**       | `HTTP 429 Too Many Requests` | Gửi request quá dồn dập, vượt ngưỡng cho phép của server Tiki. | - Kiểm soát số luồng<br/>- Thêm random sleep giữa request.<br>- Backoff khi bị lỗi. |
| **Scale data**          | `404 Not Found`              | ID sản phẩm trong Input CSV đã cũ, k còn lấy được data.        | - Sây là kết quả hợp lệ.<br>- Hệ thống ghi nhận vào log để xem sau nếu cần.   |
| **Encodingy**           | vd:`\u1ed3 `->`ồ`           | `json` ép kiểu về ASCII để tương thích                           | - Cấu hình ensure_ascii=False<br>                                                         |
| **Network Instability** | `TimeoutError`               | Mạng chập chờn hoặc server phản hồi chậm/ngắt kết nối.         | - Cấu hình timeout.<br>- Cơ chế retry ngay cho request thất bại.                      |

## Chi tiết thực hiện

### 1. Tối ưu tốc độ

Estimation:

> Got 50 products in 19.112220525741577 seconds

=> Sử dụng thư viện `requests` (Sync). Tốc độ chậm do cơ chế Blocking I/O (CPU phải chờ Network).

* **Hướng cải tiến:** Chuyển đổi sang kiến trúc async (bất đồng bộ).
* **Kết quả:** Tốc độ xử lý tăng gấp **10-20 lần**. Hệ thống có thể xử lý nhiều request trên 1 luồng.
  > Got 50 products in 1.108856439590454 seconds. Est for 200000: 1.2320627106560602 hours
  >

### 2. Xử lí lỗi

Để không mất mát dữ liệu:

- Ghi log ra file jsonl kèm timestamp và lí do lỗi
- Checkpoint: Checkpoint theo batch index
  - Cho phép resume (chạy tiếp) khi có sự cố
- Retry:
  - Retry trong từng request tùy theo loại lỗi
  - Retry hàng loạt dựa vào log file

## Key Decisions

#### Async thay vì Multi-threading?

* Web Crawling là tác vụ **I/O Bound** (chờ mạng là chính), không phải CPU Bound.
* **Vấn đề của Thread:** Python có GIL (Global Interpreter Lock), tạo OS threads tốn nhiều RAM + chi phí context switching cao.
* **Lợi ích Asyncio:**

  - Sử dụng 1 thread event loop
  - Cost RAM thấp, không có Context Switching overhead

  => phù hợp duy trì nghìn kết nối mạng đồng thời.

#### `aiohttp` ?

* `requests`: Là thư viện đồng bộ (Blocking), sẽ chặn Event Loop -> Không dùng được.
* `aiohttp`: Thư viện chuyên Async, tối ưu hóa tốt cho Client Session, Connection Pooling,...

#### Dùng `Semaphore` thay vì chia nhỏ batch (Sub-batching)?

* **Cách tiếp cận ban đầu:** Chia 1000 items thành các nhóm nhỏ 20 items, chạy xong nhóm 1 -> đợi -> 2.
* **Vấn đề:** Nếu trong nhóm 20 items có 1 request bị treo, cả 19 request còn lại đã xong cũng phải chờ theo. Lãng phí tài nguyên.
* **Semaphore:** Hoạt động như một **Sliding Window**
  - Ngay khi 1 request hoàn thành, slot đó được giải phóng và request tiếp theo được nạp vào ngay lập tức.
  - Luôn duy trì tối đa throughput mà ít tốn thời gian idle time.

#### Tại sao dùng Pydantic làm schema validation?

* Thay vì viết code với hàng loạt câu lệnh `if/else` để ktra dòng dữ liệu, Pydantic cung cấp cách định nghĩa declarative.
* **Fail-fast:** Nếu cấu trúc API thay đổi, hệ thống báo lỗi ngay tại model, giúp debug nhanh và luôn đảm bảo dữ liệu đầu ra.
* Case k quá phức tạp nên dùng thử, nghe nhiều mà chưa dùng.

## Future enhancements
- [ ] Logging & code quality: Cải thiện logging (hiện đang print), review structure
- [ ] Testing: Cân nhắc viết unit test cho các hàm, kiểm tra chất lượng dữ liệu của output data 
- [ ] Production-ready: Tìm hiểu thêm các hướng 1 pj kiểu này "chuẩn production"
- [ ] Database: Viết module connector để đưa dữ liệu trực tiếp vào db thay vì lưu file JSON.
- [ ] Dockerization: Đóng gói ứng dụng thành Docker Image để dễ deploy trên Cloud/K8s.
- [ ] Data analysis: Xem dữ liệu thu được để có thêm ý tưởng thu thập & xử lí
- [ ] Proxy rotation: Tích hợp rotating để bypass Rate Limit 429.

## Lessons learned

- Bắt đầu nhỏ, code nhỏ, dữ liệu subset -> make it run, ước lượng, checkpoint project -> cải thiện ->...
- State management: logic gửi req ko phức tạp, checkpoint-log-retry-... cũng khó và quan trọng
- Trade off giữa concurrency và delay: chậm hơn 1 chút có thể bền hơn, tránh bị chặn + tổng thể k quá chênh lệch do đỡ mất công retry

## Tham khảo

- https://tiki.vn/robots.txt
  - https://scrape.do/blog/robots-txt/
- https://www.youtube.com/watch?v=nFn4_nA_yk8
- https://www.geeksforgeeks.org/websites-apps/429-error-causes-and-solutions/
